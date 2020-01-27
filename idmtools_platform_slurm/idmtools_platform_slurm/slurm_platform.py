import typing
from typing import Optional, List
from dataclasses import dataclass, field
from logging import getLogger
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import IExperiment, IHostBinaryExperiment, IWindowsExperiment, \
    ILinuxExperiment, IDockerExperiment
from idmtools_platform_slurm.platform_operations.experiment_operations import SlurmPLatformExperimentOperations
from idmtools_platform_slurm.platform_operations.simulation_operations import SlurmPLatformSimulationOperations
from idmtools_platform_slurm.slurm_operations import SlurmOperationalMode, SlurmOperations, \
    RemoteSlurmOperations, LocalSlurmOperations

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})


@dataclass(repr=False)
class SlurmPlatform(IPlatform):
    job_directory: str = field(default=None)
    mode: SlurmOperationalMode = field(default=None)
    mail_type: Optional[str] = field(default=None)
    mail_user: Optional[str] = field(default=None)

    # options for ssh mode
    remote_host: Optional[str] = field(default=None)
    remote_port: int = field(default=22)
    remote_user: Optional[str] = field(default=None)
    key_file: Optional[str] = field(default=None)

    _simulations: SlurmPLatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _experiments: SlurmPLatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _op_client: SlurmOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        super().__post_init__()
        if self.job_directory is None:
            raise ValueError("Job Directory is required")

        self.mode = SlurmOperationalMode[self.mode.upper()] if self.mode else self.mode
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

    def supported_experiment_types(self) -> List[typing.Type]:
        supported = [IExperiment, IHostBinaryExperiment, ILinuxExperiment]
        if self.__has_singularity():
            supported.append(IDockerExperiment)
        return supported

    def unsupported_experiment_types(self) -> List[typing.Type]:
        supported = [IWindowsExperiment]
        if not self.__has_singularity():
            supported.append(IDockerExperiment)
        return supported

    def post_setstate(self):
        self.__init_interfaces()
