import getpass
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
import platform
from typing import Optional, List, Dict
import os
from idmtools import __version__
from idmtools.utils.info import get_packages_list

logger = getLogger(__name__)
default_base_sir = os.getenv('IDMTOOLS_DATA_BASE_DIR', str(Path.home()))


def get_data_directory() -> str:
    return os.path.join(default_base_sir, '.local_data')


@dataclass
class SystemInformation:
    data_directory: Optional[str] = field(default=get_data_directory())
    user: Optional[str] = getpass.getuser()
    python_version: str = platform.python_version()
    python_build: str = platform.python_build()
    python_implementation = platform.python_implementation()
    python_packages: List[str] = field(default_factory=get_packages_list)
    environment_variables: Dict[str, str] = field(default_factory=lambda: os.environ)
    os_name: str = platform.system()
    hostname: str = platform.node()
    system_version: str = platform.version()
    system_architecture: str = platform.machine()
    system_processor: str = platform.processor()
    system_architecture_details: str = platform.architecture()
    default_docket_socket_path: str = '/var/run/docker.sock'
    cwd: str = os.getcwd()
    user_group_str: str = os.getenv("CURRENT_UID", "1000:1000")
    version: str = __version__


@dataclass
class LinuxSystemInformation(SystemInformation):
    user_group_str: str = field(default_factory=lambda: os.getenv("CURRENT_UID", f'{os.getuid()}:{os.getgid()}'))


class WindowsSystemInformation(SystemInformation):
    default_docket_socket_path: str = '//var/run/docker.sock'


def get_system_information() -> SystemInformation:
    """
    Fetch the system-appropriate information inspection object.

    Returns:
        :class:`SystemInformation` with platform-specific implementation.
    """
    return LinuxSystemInformation() if platform.system() in ["Linux", "Darwin"] else WindowsSystemInformation()
