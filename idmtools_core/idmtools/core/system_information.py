"""
Utilities functions/classes to fetch info that is useful for troubleshooting user issues.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import getpass
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
import platform
from typing import Optional, List, Dict
import os
from idmtools.utils.info import get_packages_list

logger = getLogger(__name__)
default_base_sir = os.getenv('IDMTOOLS_DATA_BASE_DIR', str(Path.home()))


def get_data_directory() -> str:
    """
    Get our default data directory for a user.

    Returns:
        Default data directory for a user.
    """
    return os.path.join(default_base_sir, '.local_data')


def get_filtered_environment_vars(exclude=None) -> Dict[str, str]:
    """
    Get environment vars excluding a specific set.

    Args:
        exclude: If not provided, we default to using  ['LS_COLORS', 'XDG_CONFIG_DIRS', 'PS1', 'XDG_DATA_DIRS']

    Returns:
        Environment vars filtered for items specified
    """
    ret = dict()
    if exclude is None:
        exclude = ['LS_COLORS', 'XDG_CONFIG_DIRS', 'PS1', 'XDG_DATA_DIRS']
    for k, v in os.environ.items():
        if k not in exclude:
            ret[k] = v
    return ret


@dataclass
class SystemInformation:
    """
    Utility class to provide details useful in troubleshooting issues.
    """
    data_directory: Optional[str] = field(default=get_data_directory())
    user: Optional[str] = getpass.getuser()
    python_version: str = platform.python_version()
    python_build: str = platform.python_build()
    python_implementation = platform.python_implementation()
    python_packages: List[str] = field(default_factory=get_packages_list)
    environment_variables: Dict[str, str] = field(default_factory=get_filtered_environment_vars)
    os_name: str = platform.system()
    hostname: str = platform.node()
    system_version: str = platform.version()
    system_architecture: str = platform.machine()
    system_processor: str = platform.processor()
    system_architecture_details: str = platform.architecture()
    default_docket_socket_path: str = '/var/run/docker.sock'
    cwd: str = os.getcwd()
    user_group_str: str = os.getenv("CURRENT_UID", "1000:1000")
    version: str = None

    def __post_init__(self):
        """
        Load our version dynamically to prevent import issues.

        Returns:
            None
        """
        from idmtools import __version__
        self.version = __version__


@dataclass
class LinuxSystemInformation(SystemInformation):
    """
    LinuxSystemInformation adds linux specific properties.
    """
    user_group_str: str = field(default_factory=lambda: os.getenv("CURRENT_UID", f'{os.getuid()}:{os.getgid()}'))


class WindowsSystemInformation(SystemInformation):
    """
    WindowsSystemInformation adds windows specific properties.
    """
    default_docket_socket_path: str = '//var/run/docker.sock'


def get_system_information() -> SystemInformation:
    """
    Fetch the system-appropriate information inspection object.

    Returns:
        :class:`SystemInformation` with platform-specific implementation.
    """
    return LinuxSystemInformation() if platform.system() in ["Linux", "Darwin"] else WindowsSystemInformation()
