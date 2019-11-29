import typing
from typing import Optional, List
from dataclasses import dataclass, field
from logging import getLogger

from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import IExperiment, IHostBinaryExperiment, IWindowsExperiment, \
    ILinuxExperiment, IDockerExperiment
from idmtools_platform_slurm.slurm_operations import SlurmOperationalMode, SlurmOperations, \
    RemoteSlurmOperations, LocalSlurmOperations
from idmtools_platform_slurm.slurm_platform_commissioning import SlurmPlatformCommissioningOperations
from idmtools_platform_slurm.slurm_platform_io import SlurmPlatformIOOperations
from idmtools_platform_slurm.slurm_platform_metadata import SlurmPlaformMetdataOperations

logger = getLogger(__name__)


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

    io: SlurmPlatformIOOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})
    commissioning: SlurmPlatformCommissioningOperations = field(default=None, compare=False,
                                                                metadata={"pickle_ignore": True})
    metadata: SlurmPlaformMetdataOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})

    _op_client: SlurmOperations = field(default=None, metadata={"pickle_ignore": True})

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

