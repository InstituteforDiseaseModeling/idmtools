import copy
from dataclasses import dataclass, field
from logging import getLogger
from typing import List, Optional, Type
from idmtools.core import ItemType
from idmtools.core.system_information import get_data_directory
from idmtools.entities import IExperiment, IPlatform
from idmtools.entities.iexperiment import IDockerExperiment, IWindowsExperiment, IDockerGPUExperiment, \
    IHostBinaryExperiment
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.utils.entities import get_dataclass_common_fields
from idmtools_platform_local.infrastructure.docker_io import DockerIO
from idmtools_platform_local.infrastructure.service_manager import DockerServiceManager
from idmtools_platform_local.platform_operations.experiment_operations import LocalPlatformExperimentOperations
from idmtools_platform_local.platform_operations.simulation_operations import LocalPlatformSimulationOperations

logger = getLogger(__name__)

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})


supported_types = [PlatformRequirements.DOCKER, PlatformRequirements.GPU, PlatformRequirements.SHELL,
                   PlatformRequirements.NativeBinary, PlatformRequirements.LINUX]


@dataclass
class LocalPlatform(IPlatform):
    """
    Represents the platform allowing to run simulations locally.
    """

    host_data_directory: str = field(default=get_data_directory())
    network: str = field(default='idmtools')
    redis_image: str = field(default='redis:5.0.4-alpine')
    redis_port: int = field(default=6379)
    runtime: Optional[str] = field(default=None)
    redis_mem_limit: str = field(default='128m')
    redis_mem_reservation: str = field(default='64m')
    postgres_image: str = field(default='postgres:11.4')
    postgres_mem_limit: str = field(default='64m')
    postgres_mem_reservation: str = field(default='32m')
    postgres_port: Optional[str] = field(default=5432)
    workers_mem_limit: str = field(default='16g')
    workers_mem_reservation: str = field(default='128m')
    workers_image: str = field(default=None)
    workers_ui_port: int = field(default=5000)
    heartbeat_timeout: int = field(default=15)
    default_timeout: int = field(default=45)
    launch_created_experiments_in_browser: bool = field(default=False)
    # allows user to specify auto removal of docker worker containers
    auto_remove_worker_containers: bool = field(default=True)

    # We use this to manage our docker containers
    _sm: Optional[DockerServiceManager] = field(**op_defaults)
    _do: DockerIO = field(**op_defaults)

    _experiments: LocalPlatformExperimentOperations = field(**op_defaults)
    _simulation: LocalPlatformSimulationOperations = field(**op_defaults)
    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types))

    def __post_init__(self):
        logger.debug("Setting up local platform")
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION}
        self.__init_interfaces()
        super().__post_init__()

    def __init_interfaces(self):
        # Start our docker services
        if self._sm is None:
            # import docker here to avoid need to do it later
            import docker
            client = docker.from_env()
            opts = get_dataclass_common_fields(self, DockerServiceManager)
            self._sm = DockerServiceManager(client, **opts)
            self._sm.create_services()
        self._do = DockerIO(self.host_data_directory)
        self._experiments = LocalPlatformExperimentOperations(platform=self)
        self._simulations = LocalPlatformSimulationOperations(platform=self)

    def cleanup(self, delete_data: bool = False, shallow_delete: bool = False, tear_down_brokers: bool = False):
        self._sm.cleanup(delete_data, tear_down_brokers=tear_down_brokers)
        self._do.cleanup(delete_data, shallow_delete=shallow_delete)

    def supported_experiment_types(self) -> List[Type]:
        return [IExperiment, IDockerExperiment, IDockerGPUExperiment]

    def unsupported_experiment_types(self) -> List[Type]:
        return [IWindowsExperiment, IHostBinaryExperiment]

    def post_setstate(self):
        self.__init_interfaces()
