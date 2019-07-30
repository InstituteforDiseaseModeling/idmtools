from idmtools.entities import IPlatform
from idmtools.entities.IPlatform import PlatformSpecification
from idmtools_platform_local.LocalPlatform import LocalPlatform

LOCAL_PLATFORM_EXAMPLE_CONFIG = """
[LOCAL]
workers = max

"""


class LocalPlatformSpecification(PlatformSpecification):

    @staticmethod
    def get_description() -> str:
        return "Provides access to the Local Platform to IDM Tools"

    @staticmethod
    def get(configuration: dict) -> IPlatform:
        return LocalPlatform()

    @staticmethod
    def example_configuration():
        return LOCAL_PLATFORM_EXAMPLE_CONFIG
