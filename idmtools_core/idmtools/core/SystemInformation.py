import getpass
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
import platform
from typing import Optional, List, Dict
import os

logger = getLogger(__name__)


def get_packages_list() -> List[str]:
    """
    Returns a list of installed packages in current environment. Currently we depend on pip for this functionality
    and since it is just used for troubleshooting, we can ignore if it errors.

    Returns:
        (List[str]): List of packages installed
    """
    try:
        from pip._internal import get_installed_distributions
        installed_packages = get_installed_distributions()
        installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    except Exception as e:
        logger.exception(e)
        logger.warning("Could not load the packages from pip")
        return ["Could not load the packages from pip"]
    return installed_packages_list


@dataclass
class SystemInformation:
    data_directory: Optional[str] = str(Path.home())
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


@dataclass
class LinuxSystemInformation(SystemInformation):
    user_id: str = field(default_factory=lambda: f'{os.getuid()}:{os.getgid()}')


class WindowsSystemInformation(SystemInformation):
    default_docket_socket_path: str = '//var/run/docker.sock'


def get_system_information() -> SystemInformation:
    """
    Fetches the system appropriate information inspection object
    Returns:
        (SystemInformation): Returns a SystemInformation with platform specific implementation
    """
    return LinuxSystemInformation() if platform.system() in ["Linux", "Darwin"] else WindowsSystemInformation()
