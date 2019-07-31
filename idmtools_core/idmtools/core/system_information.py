from dataclasses import dataclass, field
from pathlib import Path
import platform
from typing import Optional, List, Dict
import os


def get_packages_list():
    import pip
    installed_packages = pip.get_installed_distributions()
    installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])
    return installed_packages_list


@dataclass
class SystemInformation:
    data_directory: Optional[str] = str(Path.home())
    user: Optional[str] = None
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
    user: str = field(default_factory=lambda: f'{os.getuid()}:{os.getgid()}')


class WindowsSystemInformation(SystemInformation):
    default_docket_socket_path: str = '//var/run/docker.sock'


def get_system_information():
    return LinuxSystemInformation() if platform in ["linux", "linux2", "darwin"] else WindowsSystemInformation()
