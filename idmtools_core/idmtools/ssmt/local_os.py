import platform
import getpass


class LocalOS:
    """
    A Central class for representing values whose proper access methods may differ between platforms.
    """

    class UnknownOS(Exception):
        pass

    WINDOWS = 'win'
    LINUX = 'lin'
    MAC = 'mac'
    ALL = (WINDOWS, LINUX, MAC)
    OPERATING_SYSTEMS = {
        'windows': {
            'name': WINDOWS,
            'username': getpass.getuser()
        },
        'linux': {
            'name': LINUX,
            'username': getpass.getuser()
        },
        'darwin': {
            'name': MAC,
            'username': getpass.getuser()
        }
    }

    _os = platform.system().lower()
    if not _os in OPERATING_SYSTEMS.keys():
        raise UnknownOS("Operating system %s is not currently supported." % platform.system())

    username = OPERATING_SYSTEMS[_os]['username']
    name = OPERATING_SYSTEMS[_os]['name']
