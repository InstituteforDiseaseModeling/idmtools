"""idmtools local platform plugin spec.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Type

from idmtools.entities.iplatform import IPlatform
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl


LOCAL_PLATFORM_EXAMPLE_CONFIG = """
[LOCAL]
# The host data directory. Optional. Defaults to {HOME}/.local_data
# host_data_directory = /home/ccollins/.local_data
# Timeout of tasks submissions to local platform
default_timeout: int = 30
# Items related to internals of the local platform. Most likely you want to use the defaults
#
# Which work image to use
workers_image: str = 'docker-staging.packages.idmod.org:latest'
# Port to display UI (ie the portion after colon in default URL http://localhost:5000)
workers_ui_port int = 5000
# This sets the max memory for workers container
# see https://docs.docker.com/compose/compose-file/compose-file-v2/#cpu-and-other-resources#specifying-byte-values
# for supported units
workers_mem_limit = '16g'
# Set mem reserved work worker
workers_mem_reservation = '128m'
# How many seconds without communication before we consider redis dead?
heartbeat_timeout = 10
# Whether to launch created experiments in the local ui on creation
launch_created_experiments_in_browser = False
# Docker runtime. On GPU Machines you may want to use nvidia instead of the default
runtime = 'runc'
# Name of idmtools local network
network = 'idmtools'
# redis config
redis_image= 'redis:5.0.4-alpine'
redis_port = 6379
redis_mem_limit = '128m'
redis_mem_reservation: str = '64m'
# Postgres settings
postgres_image = 'postgres:11.4'
postgres_mem_limit = '64m'
postgres_mem_reservation = '32m'
postgres_port = 5432
# Only set this in environments where you need to run as another user. For example, in linux systems
# where you must sudo to run as root you would want to do use this setting to run the container as
# you by getting your user id and group id id -u, id -g and replacing 1000 in the below with the values
# run_as = "1000:1000"
#
# This setting controls whether to remove docker based worker containers
# You might want this to troubleshoot containers after failures in execiton
auto_remove_worker_containers = False
# Enables singularity support. This requires elevated privileges for the worker containers and should only be used when using singularity
# Warning this is a BETA Feature!
enable_singularity_support = False
"""


class LocalPlatformSpecification(PlatformSpecification):
    """
    Provide plugin spec for the LocalPlatform.
    """

    @get_description_impl
    def get_description(self) -> str:
        """Get plugin description."""
        return "Provides access to the Local Platform to IDM Tools"

    @get_platform_impl
    def get(self, **configuration) -> IPlatform:
        """
        Build our local platform from the passed in configuration object.

        We do our import of platform here to avoid any weird import issues on plugin load.

        Args:
            configuration: COnfiguration to use with local platform.

        Returns:
            Local platform object created.
        """
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        """Get our example configuration."""
        return LOCAL_PLATFORM_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type['LocalPlatform']:  # noqa: F821
        """Get local platform type."""
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_platform_local import __version__
        return __version__
