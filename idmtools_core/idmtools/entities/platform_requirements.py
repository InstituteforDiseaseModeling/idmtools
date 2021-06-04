"""
Defines our PlatformRequirements enum.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from enum import Enum


class PlatformRequirements(Enum):
    """
    Defines possible requirements a task could need from a platform.
    """
    SHELL = "shell"  # Shell commands like ls -al
    NativeBinary = "NativeBinary"  # Run a user-provided binary
    LINUX = "Linux"  # Linux only binaries
    WINDOWS = "windows"   # windows only binaries
    GPU = "gpu"  # GPU support
    PYTHON = "python"  # Python(on host) commands
    DOCKER = "docker"  # Can you run docker commands
    SINGULARITY = "singularity"
