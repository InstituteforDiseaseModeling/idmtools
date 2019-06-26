from enum import Enum
from idmtools.entities import IPlatform
from idmtools.platforms.COMPSPlatform import COMPSPlatform
from idmtools.platforms.LocalPlatform import LocalPlatform

# Dynamically create enum PlatformType
# PlatformType = Enum('PlatformType', {p.__name__: p for p in IPlatform.__subclasses__()})
# PlatformType = type('Enum', (), {p.__name__: p for p in IPlatform.__subclasses__()})


class PlatformType(Enum):
    COMPSPlatform = COMPSPlatform
    LocalPlatform = LocalPlatform
