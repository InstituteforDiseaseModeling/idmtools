"""idmtools local platform.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
from dataclasses import dataclass, field
from logging import getLogger
from typing import List, Optional
from idmtools.core import ItemType
from idmtools.core.system_information import get_data_directory
from idmtools.entities.iplatform import IPlatform
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


@dataclass(repr=False)
class LocalPlatform(IPlatform):
    """
    Represents the platform allowing to run simulations locally.
    """

    #: Directory where data for local platform such as files and postgres data will be stored
    host_data_directory: str = field(default=get_data_directory(), metadata={"help": "Where to store the local platform files"})
    #: Name of the docker network to use
    network: str = field(default='idmtools')
    #: What redis image should we use
    redis_image: str = field(default='redis:5.0.9-alpine')
    #: Port for redis to bind to
    redis_port: int = field(default=6379)
    #: Runtime. Defaults to runc, but can be set to nvidia-docker
    runtime: Optional[str] = field(default=None)
    #: Memory limit for redis
    redis_mem_limit: str = field(default='128m')
    #: How much memory should redis preallocate
    redis_mem_reservation: str = field(default='64m')
    #: Postgres image to use
    postgres_image: str = field(default='postgres:11.9')
    #: Postgres memory limit
    postgres_mem_limit: str = field(default='64m')
    #: How much memory should postgres reserve
    postgres_mem_reservation: str = field(default='32m')
    #: What port should postgres listen to
    postgres_port: Optional[str] = field(default=5432)
    #: Memory limit for workers
    workers_mem_limit: str = field(default='16g', metadata={"help": "Memory limits for the workers (16g = 16 Gigabytes)"})
    #: How much memory should the workers pre-allocate
    workers_mem_reservation: str = field(default='128m')
    #: Workers image to use. Defaults to version compatible with current idmtools version
    workers_image: str = field(default=None)
    #: Workers UI port
    workers_ui_port: int = field(default=5000)
    #: Heartbeat timeout
    heartbeat_timeout: int = field(default=15)
    #: Default timeout when talking to local platform
    default_timeout: int = field(default=45, metadata={"help": "Timeout (in seconds) when communicating with the local platform"})
    #: Launch experiments created in the browser
    launch_created_experiments_in_browser: bool = field(default=False)
    #: allows user to specify auto removal of docker worker containers
    auto_remove_worker_containers: bool = field(default=True)
    #: Enables singularity support. This requires elevated privileges on docker and should only be used when using singularity within workflows. This feature is in BETA so it may be unstable
    enable_singularity_support: bool = field(default=False)

    # We use this to manage our docker containers
    _sm: Optional[DockerServiceManager] = field(**op_defaults, repr=False, init=False)
    _do: DockerIO = field(**op_defaults, repr=False, init=False)

    _experiments: LocalPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulation: LocalPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types),
                                                           repr=False, init=False)

    def __post_init__(self):
        """Constructor."""
        logger.debug("Setting up local platform")
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION}
        self.__init_interfaces()
        super().__post_init__()

    def __init_interfaces(self):
        """
        Create our interfaces.

        Here, we try to load the service manager. If not defined, we create it and assure all our containers are running before continuing.
        """
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
        """
        Cleanup the platform.

        If delete data is true, the local platform data is deleted.
        If shallow delete is true, just the data within the local platform data directory is deleted.
        If tear down brokers is true, the task brokers talking to the server are destroyed.

        Args:
            delete_data: Should data be deleted
            shallow_delete: Should just the files be deleted
            tear_down_brokers: Should we destroy our brokers
        """
        self._sm.cleanup(delete_data, tear_down_brokers=tear_down_brokers)
        self._do.cleanup(delete_data, shallow_delete=shallow_delete)

    def post_setstate(self):
        """Post set-state."""
        self.__init_interfaces()
