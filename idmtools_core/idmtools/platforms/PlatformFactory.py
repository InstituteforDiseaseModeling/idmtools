from enum import Enum
# TODO Refactor to use plugins
from idmtools_platform_comps.COMPSPlatform import COMPSPlatform
from idmtools_platform_local.local_platform import LocalPlatform


class PlatformType(Enum):
    COMPSPlatform = COMPSPlatform
    LocalPlatform = LocalPlatform
    #TestPlatform = TestPlatform


class PlatformFactory:
    """
    Platform factory: return platform instance bassed on the type
    """

    @staticmethod
    def get_platform(platform_type=PlatformType.COMPSPlatform, **kwargs):
        """

        Args:
            platform_type: different type of platform
            **kwargs: parameters used to create platform

        Returns: instance of the Platform

        """
        if isinstance(platform_type, str):
            platform_type = PlatformType[platform_type]

        # get platform class
        platform_cls = platform_type.value

        # create platform
        platform = platform_cls(**kwargs)

        return platform
