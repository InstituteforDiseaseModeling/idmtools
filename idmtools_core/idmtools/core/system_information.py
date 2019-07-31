from abc import abstractmethod, ABC
from pathlib import Path
from sys import platform
from typing import Optional
import os


class SystemInformation(ABC):

    @staticmethod
    def get_data_directory() -> Optional[str]:
        return str(Path.home())

    @abstractmethod
    def get_user(self) -> Optional[str]:
        pass


class LinuxSystemInformation(SystemInformation):

    def get_user(self) -> Optional[str]:
        """
        Returns a user/group string for executing docker containers as the correct user

        For example
        '1000:1000'
        Returns:
            (str): Container user id and group id of the current user
        """
        return f'{os.getuid()}:{os.getgid()}'


class WindowsSystemInformation(SystemInformation):

    def get_user(self) -> Optional[str]:
        """
        On the windows platform, we don't need a user for docker

        Returns:
            (None): Returns none meaning there is no user id to pass along
        """
        return None


def get_system_information():
    return LinuxSystemInformation() if platform in ["linux", "linux2",
                                             "darwin"] else WindowsSystemInformation()