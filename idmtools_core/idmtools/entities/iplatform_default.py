"""

Here we define platform default interface.

Currently we use this for defaults in analyzer manager, but later we can extend to other default that need to be used lazily

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from dataclasses import dataclass, field


@dataclass
class IPlatformDefault:
    """

    Represents default configuration for different types.
    """
    pass


def default_cpu_count():
    """

    Default value for cpu count. We have to wrap this so it doesn't load during plugin init.

    Returns:
        Default cpu count
    """
    from idmtools import IdmConfigParser
    return int(IdmConfigParser().get_option('COMMON', 'max_workers', os.cpu_count()))


@dataclass
class AnalyzerManagerPlatformDefault(IPlatformDefault):
    """
    Represents defaults for the AnalyzerManager.
    """
    max_workers: int = field(default_factory=default_cpu_count)
