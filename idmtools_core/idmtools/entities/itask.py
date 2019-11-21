from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.entities.command_line import TCommandLine


class PlatformRequirement(Enum):
    GPU = "gpu"
    DOCKER = "docker"
    WINDOWS = "win"
    LINUX = "linux"
    PYTHON_SCRIPTING = "python"
    SHELL_CMD = "cmd"


@dataclass
class ITask(IAssetsEnabled, ABC):
    command: TCommandLine = field(default=None)
    platform_requirements: List[PlatformRequirement] = field(default_factory=lambda: [PlatformRequirement.SHELL_CMD])
