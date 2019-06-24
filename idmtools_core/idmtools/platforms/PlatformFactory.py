from idmtools.platforms import PlatformType


class PlatformFactory:

    @staticmethod
    def get_platform(platform_type=PlatformType.COMPSPlatform, **kwargs):
        if isinstance(platform_type, str):
            platform_type = PlatformType[platform_type]

        platform = platform_type.value(**kwargs)  # if defined by enum.Enum
        # platform = platform_type(**kwargs)          # if defined by type

        return platform

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
