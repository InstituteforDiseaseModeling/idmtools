from enum import Enum
from idmtools.platforms import LocalPlatform, COMPSPlatform
from tests.utils.TestPlatform import TestPlatform


class PlatformType(Enum):
    COMPSPlatform = COMPSPlatform
    LocalPlatform = LocalPlatform
    TestPlatform = TestPlatform


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
