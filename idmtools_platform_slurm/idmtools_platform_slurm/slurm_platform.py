"""
Here we implement the SlurmPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Optional, Any, Dict
from dataclasses import dataclass, field, fields
from logging import getLogger
from idmtools.entities.iplatform import IPlatform
from idmtools.core import ItemType
from idmtools_platform_slurm.platform_operations.json_metadata_operations import JSONMetadataOperations
from idmtools_platform_slurm.platform_operations.asset_collection_operations import \
    SlurmPlatformAssetCollectionOperations
from idmtools_platform_slurm.platform_operations.experiment_operations import SlurmPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.simulation_operations import SlurmPlatformSimulationOperations
from idmtools_platform_slurm.slurm_operations.operations_interface import SlurmOperations

from idmtools_platform_slurm.slurm_operations.slurm_constants import SlurmOperationalMode
from idmtools_platform_slurm.platform_operations.suite_operations import SlurmPlatformSuiteOperations

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})
CONFIG_PARAMETERS = ['ntasks', 'partition', 'nodes', 'mail_type', 'mail_user', 'ntasks_per_core', 'cpus_per_task', 'mem_per_cpu', 'time',
                     'account', 'mem', 'exclusive', 'requeue', 'sbatch_custom', 'max_running_jobs']


@dataclass(repr=False)
class SlurmPlatform(IPlatform):
    job_directory: str = field(default=None)
    mode: SlurmOperationalMode = field(default=None)

    # region: Resources request

    # choose e-mail type
    mail_type: Optional[str] = field(default=None, metadata=dict(sbatch=True))

    # send e=mail notification
    # TODO Add Validations here from https://slurm.schedmd.com/sbatch.html#OPT_mail-type
    mail_user: Optional[str] = field(default=None, metadata=dict(sbatch=True))

    # How many nodes to be used
    nodes: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # Num of tasks
    ntasks: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # CPU # per task
    cpus_per_task: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # Task # per core
    ntasks_per_core: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # Maximum of running jobs(Per experiment)
    max_running_jobs: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # Memory per core: MB of memory
    mem: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # Memory per core: MB of memory
    mem_per_cpu: Optional[int] = field(default=None, metadata=dict(sbatch=True))

    # Which partition to use
    partition: Optional[str] = field(default=None, metadata=dict(sbatch=True))

    # Limit time on this job hrs:min:sec
    time: str = field(default=None, metadata=dict(sbatch=True))

    # if set to something, jobs will run with the specified account in slurm
    account: str = field(default=None, metadata=dict(sbatch=True))

    # Allocated nodes can not be shared with other jobs/users
    exclusive: bool = field(default=False, metadata=dict(sbatch=True))

    # Specifies that the batch job should be eligible for requeuing
    requeue: bool = field(default=True, metadata=dict(sbatch=True))

    # Default retries for jobs
    retries: int = field(default=1, metadata=dict(sbatch=False))

    # Pass custom commands to sbatch generation script
    sbatch_custom: Optional[str] = field(default=None, metadata=dict(sbatch=True))

    # modules to be load
    modules: list = field(default_factory=list, metadata=dict(sbatch=True))

    # endregion

    _suites: SlurmPlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _experiments: SlurmPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: SlurmPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _assets: SlurmPlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)
    _metas: JSONMetadataOperations = field(**op_defaults, repr=False, init=False)
    _op_client: SlurmOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        self.mode = SlurmOperationalMode[self.mode.upper()] if self.mode else self.mode
        self.__init_interfaces()
        self.supported_types = {ItemType.SUITE, ItemType.EXPERIMENT, ItemType.SIMULATION}
        super().__post_init__()
        if self.job_directory is None:
            raise ValueError("Job Directory is required.")

    def __init_interfaces(self):
        if self.mode == SlurmOperationalMode.SSH:
            # from idmtools_platform_slurm.slurm_operations.remote_operations import RemoteSlurmOperations
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
