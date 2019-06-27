from enum import Enum
from idmtools.platforms import LocalPlatform, COMPSPlatform


class PlatformType(Enum):
    COMPSPlatform = COMPSPlatform
    LocalPlatform = LocalPlatform


class PlatformFactory:

    @staticmethod
    def get_platform(platform_type=PlatformType.COMPSPlatform, **kwargs):
        if isinstance(platform_type, str):
            platform_type = PlatformType[platform_type]

        # get platform class
        platform_cls = platform_type.value

        # create platform
        platform = platform_cls(**kwargs)

        return platform
