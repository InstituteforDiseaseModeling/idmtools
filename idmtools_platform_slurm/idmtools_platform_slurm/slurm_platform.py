"""
Here we implement the SlurmPlatform object.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from typing import Optional, Any, Dict, Union, List
from dataclasses import dataclass, field, fields
from logging import getLogger
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.platform_operations.asset_collection_operations import \
    SlurmPlatformAssetCollectionOperations
from idmtools_platform_slurm.platform_operations.experiment_operations import SlurmPlatformExperimentOperations
from idmtools_platform_slurm.platform_operations.simulation_operations import SlurmPlatformSimulationOperations
from idmtools_platform_slurm.slurm_operations import SlurmOperations, SlurmOperationalMode, RemoteSlurmOperations, \
    LocalSlurmOperations

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})


@dataclass(repr=False)
class SlurmPlatform(IPlatform):
    job_directory: str = field(default=None)
    mode: SlurmOperationalMode = field(default=None)

    # region: Resources request

    # choose e-mail type
    mail_type: Optional[str] = field(default=None, metadata=dict(sbatch=True))

    # send e=mail notification
    mail_user: Optional[str] = field(default=None, metadata=dict(sbatch=True))

    # How many nodes to be used
    nodes: int = field(default=1, metadata=dict(sbatch=True))

    # Num of tasks
    ntasks: int = field(default=1, metadata=dict(sbatch=True))

    # CPU # per task
    cpu_per_task: int = field(default=1, metadata=dict(sbatch=True))

    # Memory per core: MB of memory
    mem_per_cpu: int = field(default=8192, metadata=dict(sbatch=True))

    # Which partition to use
    partition: str = field(default='cpu_short', metadata=dict(sbatch=True))

    # Limit time on this job hrs:min:sec
    time_limit: str = field(default=None, metadata=dict(sbatch=True))

    # if set to something, jobs will run with the specified account in slurm
    account: str = field(default=None, metadata=dict(sbatch=True))

    # Allocated nodes can not be shared with other jobs/users
    exclusive: bool = field(default=False, metadata=dict(sbatch=True))

    # Specifies that the batch job should be eligible for requeuing
    requeue: bool = field(default=False, metadata=dict(sbatch=True))

    # modules to be load
    modules: list = field(default_factory=list, metadata=dict(sbatch=True))

    # endregion

    # options for ssh mode
    remote_host: Optional[str] = field(default=None)
    remote_port: int = field(default=22)
    remote_user: Optional[str] = field(default=None)
    key_file: Optional[str] = field(default=None)

    _experiments: SlurmPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: SlurmPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _assets: SlurmPlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)
    _op_client: SlurmOperations = field(**op_defaults, repr=False, init=False)

    # make Property available
    _experiment_dir: str = field(default=None)

    def __post_init__(self):
        self.mode = SlurmOperationalMode[self.mode.upper()] if self.mode else self.mode
        self.__init_interfaces()
        self.supported_types = {ItemType.SUITE, ItemType.EXPERIMENT, ItemType.SIMULATION}
        super().__post_init__()
        if self.job_directory is None:
            raise ValueError("Job Directory is required.")

    def __init_interfaces(self):
        if self.mode == SlurmOperationalMode.SSH:
            if self.remote_host is None or self.remote_user is None:
                raise ValueError("remote_host, remote_user and key_file are required configuration parameters "
                                 "when the mode is SSH")
            self._op_client = RemoteSlurmOperations(platform=self, hostname=self.remote_host,
                                                    username=self.remote_user, key_file=self.key_file,
                                                    port=self.remote_port)
        else:
            self._op_client = LocalSlurmOperations(platform=self)

        self._experiments = SlurmPlatformExperimentOperations(platform=self)
        self._simulations = SlurmPlatformSimulationOperations(platform=self)
        self._assets = SlurmPlatformAssetCollectionOperations(platform=self)

    def __has_singularity(self):
        """
        Do we support singularity.
        TODO: this is left over from existing repo. Not sure if we really need this at moment.
        Returns:
        """
        # TODO Full Implementation
        return False

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
        attrs = set(vars(self).keys())
        config_dict = {k: getattr(self, k) for k in attrs.intersection(self.slurm_fields)}
        config_dict.update(kwargs)
        return config_dict
