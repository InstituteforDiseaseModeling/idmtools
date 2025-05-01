"""
Here we implement the SlurmPlatform object.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import subprocess
from typing import Optional, Any, Dict, List, Union, Literal
from dataclasses import dataclass, field, fields
from logging import getLogger
from idmtools.core import ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_file.file_platform import FilePlatform
from idmtools_platform_slurm.platform_operations.json_metadata_operations import SlurmJSONMetadataOperations
from idmtools_platform_slurm.platform_operations.asset_collection_operations import \
    SlurmPlatformAssetCollectionOperations
from idmtools_platform_slurm.platform_operations.experiment_operations import SlurmPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.simulation_operations import SlurmPlatformSimulationOperations
from idmtools_platform_slurm.platform_operations.suite_operations import SlurmPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import get_max_array_size
from idmtools_platform_slurm.slurm_operations.slurm_operations import SlurmOperations

from idmtools_platform_slurm.utils.slurm_job import run_script_on_slurm, slurm_installed

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})
CONFIG_PARAMETERS = ['ntasks', 'partition', 'nodes', 'mail_type', 'mail_user', 'ntasks_per_core', 'cpus_per_task',
                     'mem_per_cpu', 'time', 'constraint', 'account', 'mem', 'exclusive', 'requeue', 'sbatch_custom',
                     'max_running_jobs', 'array_batch_size', 'mpi_type']


@dataclass(repr=False)
class SlurmPlatform(FilePlatform):
    # region: Resources request

    # choose e-mail type
    mail_type: Optional[str] = field(default=None, metadata=dict(sbatch=True, help="e-mail type"))

    # send e=mail notification
    # TODO Add Validations here from https://slurm.schedmd.com/sbatch.html#OPT_mail-type
    mail_user: Optional[str] = field(default=None, metadata=dict(sbatch=True, help="e-mail address"))

    # How many nodes to be used
    nodes: Optional[int] = field(default=None, metadata=dict(sbatch=True, help="Number of nodes"))

    # Num of tasks
    ntasks: Optional[int] = field(default=None, metadata=dict(sbatch=True, help="Number of tasks"))

    # CPU # per task
    cpus_per_task: Optional[int] = field(default=None, metadata=dict(sbatch=True, help="Number of CPUs per task"))

    # Task # per core
    ntasks_per_core: Optional[int] = field(default=None, metadata=dict(sbatch=True, help="Number of tasks per core"))

    # Maximum of running jobs(Per experiment)
    max_running_jobs: Optional[int] = field(default=100, metadata=dict(sbatch=True, help="Maximum of running jobs"))

    # Memory per core: MB of memory
    mem: Optional[int] = field(default=None, metadata=dict(sbatch=True, help="Memory per core"))

    # Memory per core: MB of memory
    mem_per_cpu: Optional[int] = field(default=None, metadata=dict(sbatch=True, help="Memory per CPU"))

    # Which partition to use
    partition: Optional[str] = field(default=None, metadata=dict(sbatch=True, help="Partition"))

    # Specify compute node
    constraint: Optional[str] = field(default=None, metadata=dict(sbatch=True, help="Constraint"))

    # Limit time on this job hrs:min:sec
    time: str = field(default=None, metadata=dict(sbatch=True, help="Limit time on this job"))

    # if set to something, jobs will run with the specified account in slurm
    account: str = field(default=None, metadata=dict(sbatch=True, help="Account"))

    # Allocated nodes can not be shared with other jobs/users
    exclusive: bool = field(default=False, metadata=dict(sbatch=True, help="Exclusive"))

    # Specifies that the batch job should be eligible for requeuing
    requeue: bool = field(default=True, metadata=dict(sbatch=True, help="Requeue"))

    # Default retries for jobs
    retries: int = field(default=1, metadata=dict(sbatch=False, help="Default retries for jobs"))

    # Pass custom commands to sbatch generation script
    sbatch_custom: Optional[str] = field(default=None, metadata=dict(sbatch=True, help="Custom sbatch commands"))

    # modules to be load
    modules: list = field(default_factory=list, metadata=dict(sbatch=True, help="Modules to be loaded"))

    # Specifies default setting of whether slurm should fail if item directory already exists
    dir_exist_ok: bool = field(default=False, repr=False, compare=False, metadata=dict(help="Directory exist ok"))

    # Set array max size for Slurm job
    array_batch_size: int = field(default=None, metadata=dict(sbatch=False, help="Array batch size"))

    # determine if run script as Slurm job
    run_on_slurm: bool = field(default=False, repr=False, compare=False, metadata=dict(help="Run script as Slurm job"))

    # mpi type: default to pmi2 for older versions of MPICH or OpenMPI or an MPI library that explicitly requires PMI2
    mpi_type: Optional[Literal['pmi2', 'pmix', 'mpirun']] = field(default="pmi2", metadata=dict(sbatch=True,
                                                                                                help="MPI types ('pmi2', 'pmix' for slurm MPI, 'mpirun' for independently MPI)"))

    # endregion

    _suites: SlurmPlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _experiments: SlurmPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: SlurmPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _assets: SlurmPlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)
    _metas: SlurmJSONMetadataOperations = field(**op_defaults, repr=False, init=False)
    _op_client: SlurmOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        super().__post_init__()
        self.__init_interfaces()

        # check max_array_size from slurm configuration
        self._max_array_size = None
        if slurm_installed():
            self._max_array_size = get_max_array_size()

        if self.mpi_type.lower() not in {'pmi2', 'pmix', 'mpirun'}:
            raise ValueError(f"Invalid mpi_type '{self.mpi_type}'. Allowed values are 'pmi2', 'pmix', or 'mpirun'.")

        # check if run script as a slurm job
        r = run_script_on_slurm(self, run_on_slurm=self.run_on_slurm)
        if r:
            exit(0)  # finish the current workflow

    def __init_interfaces(self):
        self._op_client = SlurmOperations(platform=self)
        self._suites = SlurmPlatformSuiteOperations(platform=self)
        self._experiments = SlurmPlatformExperimentOperations(platform=self)
        self._simulations = SlurmPlatformSimulationOperations(platform=self)
        self._assets = SlurmPlatformAssetCollectionOperations(platform=self)
        self._metas = SlurmJSONMetadataOperations(platform=self)

    @property
    def slurm_fields(self):
        """
        Get list of fields that have metadata sbatch.
        Returns:
            Set of fields that have sbatch metadata
        """
        return set(f.name for f in fields(self) if "sbatch" in f.metadata and f.metadata["sbatch"])

    def get_slurm_configs(self, **kwargs) -> Dict[str, Any]:
        """
        Identify the Slurm config parameters from the fields.
        Args:
            kwargs: additional parameters
        Returns:
            slurm config dict
        """
        config_dict = {k: getattr(self, k) for k in self.slurm_fields}
        config_dict.update(kwargs)
        return config_dict

    def create_batch_file(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        self._op_client.create_batch_file(item, **kwargs)

    def get_job_id(self, item_id: str, item_type: ItemType) -> List:
        """
        Retrieve the job id for item that had been run.
        Args:
            item_id: id of experiment/simulation
            item_type: ItemType (Experiment or Simulation)
        Returns:
            List of slurm job ids
        """
        if item_type not in (ItemType.EXPERIMENT, ItemType.SIMULATION):
            raise RuntimeError(f"Not support item type: {item_type}")

        item_dir = self.get_directory_by_id(item_id, item_type)
        job_id_file = item_dir.joinpath('job_id.txt')
        if not job_id_file.exists():
            logger.debug(f"{job_id_file} not found.")
            return None

        job_id = open(job_id_file).read().strip()
        return job_id.split('\n')

    def submit_job(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Submit a Slurm job.
        Args:
            item: idmtools Experiment or Simulation
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        if isinstance(item, Experiment):
            working_directory = self.get_directory(item)
            subprocess.run(['bash', 'batch.sh'], stdout=subprocess.PIPE, cwd=str(working_directory))
        elif isinstance(item, Simulation):
            pass
        else:
            raise NotImplementedError(f"Submit job is not implemented on SlurmPlatform.")
