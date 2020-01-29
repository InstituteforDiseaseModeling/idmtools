import typing
from typing import Optional, List
from dataclasses import dataclass, field
from logging import getLogger
from idmtools.entities.iplatform import IPlatform
from idmtools_platform_slurm.platform_operations.experiment_operations import SlurmPLatformExperimentOperations
from idmtools_platform_slurm.platform_operations.simulation_operations import SlurmPLatformSimulationOperations
from idmtools_platform_slurm.slurm_operations import SlurmOperationalMode, SlurmOperations, \
    RemoteSlurmOperations, LocalSlurmOperations


logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})

@dataclass
class SlurmPlatform(IPlatform):

    job_directory: str = None
    mode: SlurmOperationalMode = None
    mail_type: Optional[str] = None
    mail_user: Optional[str] = None

    # options for ssh mode
    remote_host: Optional[str] = None
    remote_port: int = 22
    remote_user: Optional[str] = None
    key_file: Optional[str] = None

    _simulations: SlurmPLatformSimulationOperations = field(**op_defaults)
    _experiments: SlurmPLatformExperimentOperations = field(**op_defaults)
    _op_client: SlurmOperations = field(**op_defaults)

    def __post_init__(self):
        super().__post_init__()
        if self.job_directory is None:
            raise ValueError("Job Directory is required")

        self.mode = SlurmOperationalMode[self.mode.upper()]
        self.__init_interfaces()

    def __init_interfaces(self):
        if self.mode == SlurmOperationalMode.SSH:
            if self.remote_host is None or self.remote_user is None:
                raise ValueError("remote_host, remote_user and key_file are required configuration parameters "
                                 "when the mode is SSH")
            self._op_client = RemoteSlurmOperations(self.remote_host, self.remote_user, self.key_file,
                                                    port=self.remote_port)
        else:
            self._op_client = LocalSlurmOperations()
        self._simulations = SlurmPLatformSimulationOperations(self)
        self._experiments = SlurmPLatformExperimentOperations(self)

    def __has_singularity(self):
        """
        Do we support singularity
        Returns:

        """
        # TODO Full Implementation
        return False

    def post_setstate(self):
        self.__init_interfaces()

