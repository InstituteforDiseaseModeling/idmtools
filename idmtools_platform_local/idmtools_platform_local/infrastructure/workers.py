import os
import platform
import time
import requests
from dataclasses import dataclass
from logging import getLogger, DEBUG
from typing import Dict
from docker.models.containers import Container

from idmtools.core.system_information import get_system_information
from idmtools_platform_local.client.healthcheck_client import HealthcheckClient
from idmtools_platform_local.infrastructure.base_service_container import BaseServiceContainer
from idmtools_platform_local import __version__

logger = getLogger(__name__)


def get_worker_image_default():
    # determine default docker to use
    # we first check if it is nightly. Nightly will ALWAYS use staging
    if "nightly" in __version__:
        docker_repo = 'idm-docker-staging.packages.idmod.org'
    # otherwise we let the user have come control by default to docker-public
    else:
        docker_repo = f'{os.getenv("DOCKER_REPO", "idm-docker-public")}.packages.idmod.org'

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Default docker repo set to: {docker_repo}")

    default_image = f'{docker_repo}/idmtools_local_workers:{__version__.replace("+", ".")}'
    return default_image


@dataclass
class WorkersContainer(BaseServiceContainer):
    host_data_directory: str = None
    postgres_port: int = 5432
    redis_port: int = 6379
    ui_port: int = 5000
    # make this configurable and also size this to
    # size of available ram. We should probably support like 0.8 for 80% because some models, this can be
    # where they are ran
    mem_limit: str = '16g'
    mem_reservation: str = '64m'
    run_as: str = None
    debug_api: bool = True
    image: str = get_worker_image_default()
    container_name: str = 'idmtools_workers'
    data_volume_name: str = os.getenv("IDMTOOLS_WORKERS_DATA_MOUNT_BY_VOLUMENAME", None)
    config_prefix: str = 'workers_'

    def __post_init__(self):
        system_info = get_system_information()
        if self.run_as is None:
            self.run_as = system_info.user_group_str

    def get_configuration(self) -> Dict:
        logger.debug(f'Creating working container')
        if not self.data_volume_name:
            data_dir = os.path.join(self.host_data_directory, 'workers')
            os.makedirs(data_dir, exist_ok=True)
        else:
            logger.debug(f"Specifying Data directory using named volume {self.data_volume_name}")
            data_dir = f'{self.data_volume_name}'
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Worker default directory is {data_dir}")

        docker_socket = '/var/run/docker.sock'
        if os.name == 'nt':
            docker_socket = '/' + docker_socket
        worker_volumes = {
            data_dir: dict(bind='/data', mode='rw'),
            docker_socket: dict(bind='/var/run/docker.sock', mode='rw')
        }
        environment = [f'REDIS_URL=redis://idmtools_redis:{self.redis_port}',
                       f'HOST_DATA_PATH={data_dir}',
                       f'SQLALCHEMY_DATABASE_URI='
                       f'postgresql+psycopg2://idmtools:idmtools@idmtools_postgres:{self.postgres_port}/idmtools']

        if platform.system() in ["Linux", "Darwin"]:
            environment.append(f'CURRENT_UID={self.run_as}')

        if self.debug_api:
            environment.append('API_LOGGING=1')

        if self.data_volume_name:
            environment.append(f'IDMTOOLS_WORKERS_DATA_MOUNT_BY_VOLUMENAME=self.data_volume_name')

        port_bindings = self._get_optional_port_bindings(self.ui_port, 5000)
        container_config = self.get_common_config(container_name=self.container_name, image=self.image,
                                                  port_bindings=port_bindings, network=self.network,
                                                  mem_reservation=self.mem_reservation, volumes=worker_volumes,
                                                  mem_limit=self.mem_limit, environment=environment,
                                                  links=dict(idmtools_redis='redis', idmtools_postgres='postgres')
                                                  )

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Worker Config: {container_config}")
        return container_config

    def create(self, spinner=None) -> Container:
        result = super().create(spinner)
        # postgres will restart once so we should watch it again
        time.sleep(0.2)
        self.wait_on_status(result)
        start = time.time()
        while (time.time() - start) < 30:
            try:
                response = HealthcheckClient.get(HealthcheckClient.path_url)
                if response.status_code == 200:
                    response = response.json()
                    if 'db' in response and response['db']:
                        logger.debug("Local API in ready state")
                        return result
            except requests.exceptions.ConnectionError:
                pass
            time.sleep(0.25)

        raise EnvironmentError("Local Platform is not in ready state")
