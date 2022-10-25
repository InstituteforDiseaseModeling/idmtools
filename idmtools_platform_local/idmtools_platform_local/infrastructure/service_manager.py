"""idmtools service manager. Manages all our local platform services.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field, fields
import logging
import time
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from json import JSONDecodeError
from logging import getLogger
from typing import NoReturn, Dict, Optional, List, Union
from docker import DockerClient
from docker.models.containers import Container
from docker.models.networks import Network
from idmtools.core.system_information import get_data_directory, get_system_information
from idmtools.utils.decorators import optional_yaspin_load
from idmtools_platform_local.infrastructure.base_service_container import BaseServiceContainer
from idmtools_platform_local.infrastructure.postgres import PostgresContainer
from idmtools_platform_local.infrastructure.redis import RedisContainer
from idmtools_platform_local.infrastructure.workers import WorkersContainer

SERVICES = [PostgresContainer, RedisContainer, WorkersContainer]
CONTAINER_WAIT: Dict[str, List[str]] = dict(
    workers=['postgres_port', 'redis_port']
)


logger = getLogger(__name__)


@dataclass
class DockerServiceManager:
    """
    Provides single interface to manage all the local platform services.
    """
    client: DockerClient
    host_data_directory: str = get_data_directory()
    network: str = 'idmtools'
    redis_image: str = 'redis:5.0.4-alpine'
    heartbeat_timeout: int = 15
    redis_port: int = 6379
    runtime: Optional[str] = 'runc'
    redis_mem_limit: str = '256m'
    redis_mem_reservation: str = '32m'
    postgres_image: str = 'postgres:11.4'
    postgres_mem_limit: str = '128m'
    postgres_mem_reservation: str = '32m'
    postgres_port: Optional[str] = 5432
    workers_image: str = None
    workers_ui_port: int = 5000
    workers_mem_limit: str = None
    workers_mem_reservation: str = '64m'
    run_as: Optional[str] = field(default=None)
    enable_singularity_support: bool = False

    _services: Dict[str, BaseServiceContainer] = None

    def __post_init__(self):
        """Constructor."""
        self.system_info = get_system_information()
        if self.run_as is None:
            self.run_as = self.system_info.user_group_str

        if self.run_as == "0:0":
            message = "You cannot run the containers as the root user!. Please select another value for 'run_as'. "
            if self.system_info.user_group_str == "0:0":
                message += " It appears you executed a script/command as the local root user or use sudo to start the" \
                           " Local Platform. If that is the case, use the 'run_as' configuration option in your " \
                           "idmtools.ini Local Platform configuration block or initializing the Local Platform object"
            raise ValueError(message)

        self.init_services()

    def init_services(self):
        """Start all the containers we should have running."""
        self._services = dict()
        for _i, service in enumerate(SERVICES):
            sn = service.__name__.replace("Container", "").lower()
            if sn not in self._services:
                self._services[sn] = service(**self.get_container_config(service))

    def cleanup(self, delete_data: bool = False, tear_down_brokers: bool = False) -> NoReturn:
        """
        Stops the containers and removes the network.

        Optionally the postgres data container can be deleted as well as closing any active Redis connections.

        Args:
            delete_data: Delete postgres data
            tear_down_brokers: True to close redis brokers, false otherwise

        Returns:
            NoReturn
        """
        self.stop_services()

        if tear_down_brokers:
            from idmtools_platform_local.internals.workers.brokers import close_brokers
            logger.debug("Closing brokers down")
            close_brokers()

        if delete_data:
            postgres_volume = self.client.volumes.list(filters=dict(name='idmtools_local_postgres'))
            if postgres_volume:
                postgres_volume[0].remove(True)

        network = self.get_network()
        if network:
            logger.debug(f'Removing docker network: {self.network}')
            network.remove()

    @staticmethod
    def setup_broker(heartbeat_timeout):
        """Start the broker to send data to workers."""
        from idmtools_platform_local.internals.workers.brokers import setup_broker
        setup_broker(heartbeat_timeout)

    @staticmethod
    def restart_brokers(heartbeat_timeout):
        """Restart brokers talking to workers."""
        from idmtools_platform_local.internals.workers.brokers import setup_broker, close_brokers
        close_brokers()
        setup_broker(heartbeat_timeout)

    @optional_yaspin_load(text="Ensure IDM Tools Local Platform services are loaded")
    def create_services(self, spinner=None) -> NoReturn:
        """
        Create all the components of local platform.

        Our architecture is as depicted in the UML diagram below

        .. uml::

            @startuml
            database "Postgres Container" as db
            node "Redis Container"as redis
            node "Workers Container" {
                [UI] -> db
                rectangle "Python Workers" {
                    rectangle "Worker ..." as w2
                    rectangle "Worker 1" as w1
                    w1 <---> db : Get/Update Status
                    w1 <---> redis : Get task/Add Task
                    w2 <---> db
                    w2 <---> redis
                }
            }
            file "User Python Script" as u
            u ...> redis : Submit task
            u <... redis : Get result
            @enduml

        Returns:
            (NoReturn)
        """
        try:
            self.get_network()
            for _i, service in enumerate(SERVICES):
                sn = service.__name__.replace("Container", "").lower()
                # wait on services to be ready for workers
                if sn in CONTAINER_WAIT:
                    self.wait_on_ports_to_open(CONTAINER_WAIT[sn])
                attempts = 0
                while attempts < 3:
                    try:
                        self._services[sn].get_or_create(spinner)
                        break
                    except JSONDecodeError:
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"Failure to get service {sn}")
                        if attempts == 3:
                            logger.debug(f"Ran out of attempts to create {sn}")
                            raise
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"Retrying {sn}")
                        attempts += 1
            self.wait_on_ports_to_open(['workers_ui_port'])
            self.setup_broker(self.heartbeat_timeout)
        except Exception as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception(e)
            raise e

    def wait_on_ports_to_open(self, ports: List[str], wait_between_tries: Union[int, float] = 0.2, max_retries: int = 5,
                              sleep_after: Union[int, float] = 0.5) -> bool:
        """
        Polls list of port attributes(eg postgres_port, redis_port and checks if they are currently open.

        We use this to verify postgres/redis are ready for our workers

        Args:
            ports: List of port attributes
            wait_between_tries: Time between port checks
            max_retries: Max checks
            sleep_after: Sleep after all our found open(Postgres starts accepting connections before actually ready)

        Returns:
            True if ports are ready
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Waiting on the following ports to become available: {str(ports)}")
        retries = 0
        while retries <= max_retries:
            time.sleep(wait_between_tries)
            if all([self.is_port_open('127.0.0.1', getattr(self, port)) for port in ports]):
                if sleep_after > 0:
                    time.sleep(sleep_after)
                return True
            retries += 1
        logger.warning("Possible issue platform. Could not connect to server ports")
        return False

    @optional_yaspin_load(text="Stopping IDM Tools Local Platform services")
    def stop_services(self, spinner=None) -> NoReturn:
        """
        Stops all running IDM Tools services.

        Returns:
            (NoReturn)
        """
        with ThreadPoolExecutor() as pool:
            futures = []
            for service in self._services.values():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'Stopping {service.__class__.__name__}')
                pool.submit(self.stop_service_and_wait, service)
            for _done in as_completed(futures):
                pass

    def get(self, container_name: str, create=True) -> Container:
        """
        Get the server with specified name.

        Args:
            container_name: Name of container
            create: Create if it doesn't exists

        Returns:
            Container
        """
        service = self._services[container_name.lower()]
        return service.get_or_create() if create else service.get()

    def get_container_config(self, service: BaseServiceContainer, opts=None):
        """
        Get the container config for the service.

        Args:
            service: Service to get config for
            opts: Opts to Extract. Should be a fields object

        Returns:
            Container config
        """
        dest_fields = {f.name: f for f in fields(service)}
        if not opts:
            my_fields = fields(self)
        else:
            my_fields = list(opts.keys())

        prefix = ''
        if 'config_prefix' in dest_fields:
            prefix = dest_fields['config_prefix'].default

        ret = dict(client=self.client)
        for opt in my_fields:
            if opts:
                dest_name = opt.replace(prefix, "")
                if dest_name in dest_fields and opts[opt] is not None:
                    ret[dest_name] = opts[opt]
            else:
                # we are dealing with the local data class fields
                dest_name = opt.name.replace(prefix, "")
                if dest_name in dest_fields and getattr(self, opt.name, None) is not None:
                    ret[dest_name] = getattr(self, opt.name)
        return ret

    @optional_yaspin_load(text="Restarting IDM-Tools services")
    def restart_all(self, spinner=None) -> NoReturn:  # noqa: F811
        """
        Restart all the services IDM-Tools services.

        Returns:
            (NoReturn)
        """
        for service in self._services.values():
            service.restart()

    @staticmethod
    def is_port_open(host: str, port: int) -> bool:
        """
        Check if a port is open.

        Args:
            host: Host to check
            port: Port to check

        Returns:
            True if port is open, False otherwise
        """
        import socket
        from contextlib import closing
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Checking if port {port} is open on host {host}")
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            return isinstance(port, int) and sock.connect_ex((host, port)) == 0

    @staticmethod
    def stop_service_and_wait(service) -> bool:
        """
        Stop server and wait.

        Args:
            service: Service to stop

        Returns:
            True
        """
        service.stop(True)
        container = service.get()
        while container:
            time.sleep(0.1)
            container = service.get()
        return True

    def get_network(self) -> Network:
        """
        Fetches the IDM Tools network.

        Returns:
            (Network) Return Docker network object
        """
        # check that the network exists
        network = self.client.networks.list(filters=dict(name=self.network))
        # check name specifically
        network = [x for x in network if x.name == self.network]
        if not network:
            logger.debug(f'Creating network {self.network}')
            network = self.client.networks.create(self.network, driver='bridge', internal=False,
                                                  attachable=False, ingress=False, scope='local')
        else:
            network = network[0]
        return network
