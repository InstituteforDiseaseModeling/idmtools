"""
Info to determine info about Operation Systems.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import platform
import getpass


class LocalOS:
    """
    A Central class for representing values whose proper access methods may differ between platforms.
    """

    class UnknownOS(Exception):
        """
        Unknown os detected.
        """
        pass

    os_mapping = {'windows': 'win',
                  'linux': 'lin',
                  'darwin': 'mac'}

    _os = platform.system().lower()
    if _os not in os_mapping:
        raise UnknownOS("Operating system %s is not currently supported." % _os)

    username = getpass.getuser()
    name = os_mapping[_os]

    @staticmethod
    def is_window() -> bool:
        """
        Are we running on a windows system?

        Returns:
            True if on windows
        """
        return LocalOS.name == 'win'
