from idmtools.entities import IPlatform
from idmtools.entities.IPlatform import PlatformSpecification

LOCAL_PLATFORM_EXAMPLE_CONFIG = """
[LOCAL]
redis_image=redis:5.0.4-alpine
redis_port=6379
runtime=nvidia
workers_image: str = 'idm-docker-production.packages.idmod.org:latest'
workers_ui_port: int = 5000
"""


class LocalPlatformSpecification(PlatformSpecification):

    @staticmethod
    def get_description() -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @staticmethod
    def get(configuration: dict) -> IPlatform:
        from idmtools_platform_local.local_platform import LocalPlatform
        return LocalPlatform()

    @staticmethod
    def example_configuration():
        return LOCAL_PLATFORM_EXAMPLE_CONFIG
