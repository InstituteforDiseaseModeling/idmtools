"""idmtools redis service.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import platform
from dataclasses import dataclass
from logging import getLogger, DEBUG

from idmtools.core.system_information import get_system_information
from idmtools_platform_local.infrastructure.base_service_container import BaseServiceContainer

logger = getLogger(__name__)


@dataclass
class RedisContainer(BaseServiceContainer):
    """
    Provides the redis container for local platform.
    """
    host_data_directory: str = None
    mem_limit: str = '256m'
    mem_reservation: str = '64m'
    run_as: str = None
    port: int = 6379
    image: str = 'redis:5.0.4-alpine'
    data_volume_name: str = os.getenv("IDMTOOLS_REDIS_DATA_MOUNT_BY_VOLUMENAME", None)
    container_name: str = 'idmtools_redis'
    config_prefix: str = 'redis_'

    def __post_init__(self):
        """Constructor."""
        system_info = get_system_information()
        if self.run_as is None:
            self.run_as = system_info.user_group_str

    def get_configuration(self) -> dict:
        """
        Get our configuration to run redis.

        Returns:
            Redis config.
        """
        # check if we are using the host data path or using a data volume to mount data
        if self.data_volume_name:
            logger.debug(f"Specifying Data directory using named volume {self.data_volume_name}")
            data_dir = f'{self.data_volume_name}'
        else:
            data_dir = os.path.join(self.host_data_directory, 'redis-data')
            logger.debug(f'Creating redis data directory at {data_dir}')
            os.makedirs(data_dir, exist_ok=True)

        redis_volumes = {
            data_dir: dict(bind='/data', mode='rw')
        }
        port_bindings = self._get_optional_port_bindings(self.port, 6379)
        container_config = self.get_common_config(container_name=self.container_name, image=self.image,
                                                  mem_limit=self.mem_limit, mem_reservation=self.mem_reservation,
                                                  network=self.network, port_bindings=port_bindings,
                                                  volumes=redis_volumes)
        # if we are are unix based systems we should
        if platform.system() in ["Linux", "Darwin"]:
            container_config['user'] = self.run_as
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Redis Config: {container_config}")
        return container_config
