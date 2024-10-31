"""
Here we implement the SlurmPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from pathlib import Path
from typing import Optional, Any, Dict, List, Union, Literal
from dataclasses import dataclass, field, fields
from logging import getLogger
from idmtools import IdmConfigParser
from idmtools.core import ItemType, EntityStatus, TRUTHY_VALUES
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.suite import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform import IPlatform, ITEM_TYPE_TO_OBJECT_INTERFACE
from idmtools_platform_slurm.platform_operations.json_metadata_operations import JSONMetadataOperations
from idmtools_platform_slurm.platform_operations.asset_collection_operations import \
    SlurmPlatformAssetCollectionOperations
from idmtools_platform_slurm.platform_operations.experiment_operations import SlurmPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.simulation_operations import SlurmPlatformSimulationOperations
from idmtools_platform_slurm.slurm_operations.operations_interface import SlurmOperations
from idmtools_platform_slurm.slurm_operations.slurm_constants import SlurmOperationalMode
from idmtools_platform_slurm.platform_operations.suite_operations import SlurmPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmSuite, SlurmExperiment, SlurmSimulation, \
    get_max_array_size
from idmtools_platform_slurm.utils.slurm_job import run_script_on_slurm, slurm_installed

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})
CONFIG_PARAMETERS = ['ntasks', 'partition', 'nodes', 'mail_type', 'mail_user', 'ntasks_per_core', 'cpus_per_task',
                     'mem_per_cpu', 'time', 'constraint', 'account', 'mem', 'exclusive', 'requeue', 'sbatch_custom',
                     'max_running_jobs', 'array_batch_size', 'mpi_type']


@dataclass(repr=False)
class SlurmPlatform(IPlatform):
    job_directory: str = field(default=None, metadata=dict(help="Job Directory"))

    #: Needed for bridge mode
    bridged_jobs_directory: str = field(default=Path.home().joinpath(".idmtools").joinpath("singularity-bridge"),
                                        metadata=dict(help="Bridged Jobs Directory"))
    bridged_results_directory: str = field(
        default=Path.home().joinpath(".idmtools").joinpath("singularity-bridge").joinpath("results"),
        metadata=dict(help="Bridged Results Directory"))

    mode: SlurmOperationalMode = field(default=SlurmOperationalMode.LOCAL, metadata=dict(help="Slurm Operational Mode"))

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
    _metas: JSONMetadataOperations = field(**op_defaults, repr=False, init=False)
    _op_client: SlurmOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        if isinstance(self.mode, str):
            if self.mode.upper() not in [mode.value.upper() for mode in SlurmOperationalMode]:
                raise ValueError(
                    f"{self.mode} is not a value mode. Please select one of the following {', '.join([mode.value for mode in SlurmOperationalMode])}")
            self.mode = SlurmOperationalMode[self.mode.upper()]

        if not isinstance(self.mode, SlurmOperationalMode):
            raise ValueError(f"{self.mode} is not a valid mode. Please use enum {SlurmOperationalMode}")

        self.__init_interfaces()
        self.supported_types = {ItemType.SUITE, ItemType.EXPERIMENT, ItemType.SIMULATION}
        if self.job_directory is None:
            raise ValueError("Job Directory is required.")
        self.job_directory = os.path.abspath(self.job_directory)
        self.name_directory = IdmConfigParser.get_option(None, "name_directory", 'True').lower() in TRUTHY_VALUES
        self.sim_name_directory = IdmConfigParser.get_option(None, "sim_name_directory",
                                                             'False').lower() in TRUTHY_VALUES

        # check max_array_size from slurm configuration
        self._max_array_size = None
        if slurm_installed():
            self._max_array_size = get_max_array_size()

        super().__post_init__()

        # check if run script as a slurm job
        r = run_script_on_slurm(self, run_on_slurm=self.run_on_slurm)
        if r:
            exit(0)  # finish the current workflow

    def __init_interfaces(self):
        if self.mode == SlurmOperationalMode.SSH:
            raise NotImplementedError("SSH mode has not been implemented on the Slurm Platform")
        elif self.mode == SlurmOperationalMode.BRIDGED:
            from idmtools_platform_slurm.slurm_operations.bridged_operations import BridgedLocalSlurmOperations
            self._op_client = BridgedLocalSlurmOperations(platform=self)
        else:
            from idmtools_platform_slurm.slurm_operations.local_operations import LocalSlurmOperations
            self._op_client = LocalSlurmOperations(platform=self)

        self._suites = SlurmPlatformSuiteOperations(platform=self)
        self._experiments = SlurmPlatformExperimentOperations(platform=self)
        self._simulations = SlurmPlatformSimulationOperations(platform=self)
        self._assets = SlurmPlatformAssetCollectionOperations(platform=self)
        self._metas = JSONMetadataOperations(platform=self)

    def post_setstate(self):
        self.__init_interfaces()

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

    def flatten_item(self, item: IEntity, raw=False, **kwargs) -> List[object]:
        """
        Flatten an item: resolve the children until getting to the leaves.

        For example, for an experiment, will return all the simulations.
        For a suite, will return all the simulations contained in the suites experiments.

        Args:
            item: Which item to flatten
            raw: bool
            kwargs: extra parameters

        Returns:
            List of leaves
        """
        if not raw:
            interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
            idm_item = getattr(self, interface).to_entity(item)
            return super().flatten_item(idm_item)

        if isinstance(item, SlurmSuite):
            experiments = self._suites.get_children(item, parent=item, raw=True)
            children = list()
            for slurm_exp in experiments:
                children += self.flatten_item(item=slurm_exp, raw=raw)
        elif isinstance(item, SlurmExperiment):
            children = self._experiments.get_children(item, parent=item, raw=True)
            exp = Experiment()
            exp.uid = item.id
            exp.platform = self
            exp._platform_object = item
            exp.tags = item.tags

            for slurm_sim in children:
                slurm_sim.experiment = exp
                slurm_sim.platform = self
        elif isinstance(item, SlurmSimulation):
            if raw:
                children = [item]
            else:
                exp = Experiment()
                exp.uid = item.id
                exp.platform = self
                exp._platform_object = item
                exp.tags = item.tags
                sim = self._simulations.to_entity(item, parent=exp)
                sim.experiment = exp
                children = [sim]
        elif isinstance(item, Suite):
            slurm_suite = item.get_platform_object()
            slurm_suite.platform = self
            children = self.flatten_item(item=slurm_suite)
        elif isinstance(item, Experiment):
            children = item.simulations.items
        elif isinstance(item, Simulation):
            children = [item]
        else:
            raise Exception(f'Item Type: {type(item)} is not supported!')

        return children

    def validate_item_for_analysis(self, item: Union[Simulation, SlurmSimulation], analyze_failed_items=False):
        """
        Check if item is valid for analysis.

        Args:
            item: which item to verify status
            analyze_failed_items: bool

        Returns: bool
        """
        result = False

        # TODO: we may consolidate two cases into one
        if isinstance(item, SlurmSimulation):
            if item.status == EntityStatus.SUCCEEDED:
                result = True
            else:
                if analyze_failed_items and item.status == EntityStatus.FAILED:
                    result = True
        elif isinstance(item, Simulation):
            if item.succeeded:
                result = True
            else:
                if analyze_failed_items and item.status == EntityStatus.FAILED:
                    result = True
        return result

    def get_directory(self, item: Union[Suite, Experiment, Simulation]) -> Path:
        """
        Get item's path.
        Args:
            item: Suite, Experiment, Simulation
        Returns:
            item file directory
        """
        return self._op_client.get_directory(item)

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        """
        Get item's path.
        Args:
            item_id: entity id (Suite, Experiment, Simulation)
            item_type: the type of items (Suite, Experiment, Simulation)
        Returns:
            item file directory
        """
        return self._op_client.get_directory_by_id(item_id, item_type)
