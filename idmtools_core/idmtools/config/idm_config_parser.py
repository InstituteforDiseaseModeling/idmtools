import copy
import platform
from pathlib import Path
import json
import os
from configparser import ConfigParser
from logging import getLogger
from typing import Any, Dict
from idmtools.utils.info import get_help_version_url

default_config = 'idmtools.ini'

# this is the only logger that should not be defined using init_logger
logger = getLogger(__name__)
user_logger = getLogger('user')


def initialization(error=False, force=False):
    # store default value
    oerror = error

    def wrap(func):
        def wrapped_f(*args, **kwargs):
            if 'error' in kwargs:
                ferror = kwargs.pop('error')
            elif os.getenv("IDMTOOLS_ERROR_NO_CONFIG", None) is not None:
                user_logger.warning("Using IDMTOOLS_ERROR_NO_CONFIG environment variable to control behaviour of missing ini file")
                ferror = os.getenv("IDMTOOLS_ERROR_NO_CONFIG").lower() in ["1", "y", "t", "true", "yes"]
            else:
                ferror = oerror
            IdmConfigParser.ensure_init(error=ferror, force=force)
            value = func(*args, **kwargs)
            return value

        return wrapped_f

    return wrap


class IdmConfigParser:
    """
    Class that parses an INI configuration file.
    """
    _config = None
    _instance = None
    _config_path = None
    _block = None

    def __new__(cls, dir_path: str = '.', file_name: str = default_config) -> 'IdmConfigParser':
        """
        Make :class:`IdmConfigParser` creation a singleton.

        Args:
            dir_path: The INI configuration file directory.
            file_name: The INI file name.

        Returns:
            An :class:`IdmConfigParser` instance.
        """
        if not cls._instance:
            cls._instance = super(IdmConfigParser, cls).__new__(cls)
            cls._instance._load_config_file(dir_path, file_name)
        return cls._instance

    @classmethod
    def retrieve_dict_config_block(cls, field_type, section) -> Dict[str, Any]:
        import ast

        inputs = copy.deepcopy(section)
        fs = set(field_type.keys()).intersection(set(section.keys()))
        for fn in fs:
            ft = field_type[fn]
            if ft in (int, float, str):
                inputs[fn] = ft(section[fn])
            elif ft is bool:
                inputs[fn] = ast.literal_eval(section[fn])
        return inputs

    @classmethod
    @initialization
    def retrieve_settings(cls, section: str = None, field_type: Dict[str, str] = {}) -> Dict[str, str]:
        """
        Retrieve INI configuration values (to be used when updating platform fields). Call from each platform.

        Args:
            section: The INI section from which to retrieve configuration values.
            field_type: The requested data types.

        Returns:
            The configuration values as a dictionary.
        """
        # retrieve THIS platform config settings
        field_config = cls.get_section(section)

        # update field types
        field_config_updated = cls.retrieve_dict_config_block(field_config, section)
        return field_config_updated

    @classmethod
    def _find_config(cls, dir_path: str = None, file_name: str = default_config) -> None:
        """
        Recursively search for the INI configuration file starting from the **dir_path** provided
        up to the root, stopping once one is found.

        Args:
            dir_path: The directory to start looking for the INI configuration file.
            file_name: The name of the configuration file to look for.

        Returns:
            None
        """
        full_dir_path = os.path.abspath(dir_path)
        if os.path.exists(os.path.join(full_dir_path, file_name)):
            cls._config_path = os.path.join(full_dir_path, file_name)
            return cls._config_path
        else:
            dir_parent = os.path.dirname(full_dir_path)
            if dir_parent == full_dir_path:
                return None
            else:
                cls._config_path = cls._find_config(dir_parent, file_name)
                return cls._config_path

    @staticmethod
    def get_global_configuration_name() -> str:
        """
        Get Global Configuration Name

        Returns:
            On Windows, this returns %LOCALDATA%\\idmtools\\idmtools.ini
            On Mac and Linux, it returns "/home/username/.idmtools.ini'

        Raises:
            Value Error on OSs not supported
        """
        if platform.system() in ["Linux", "Darwin"]:
            ini_file = os.path.join(str(Path.home()), ".idmtools.ini")
        # On Windows, c:\users\user\AppData\Local\idmtools\idmtools.ini
        elif platform.system() in ["Windows"]:
            ini_file = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'), "idmtools", "idmtools.ini")
        else:
            raise ValueError("OS global configuration cannot be detected")
        return ini_file

    @classmethod
    def _load_config_file(cls, dir_path: str = os.getcwd(), file_name: str = default_config):
        """
        Find and then load the INI configuration file and parse it with :class:`IdmConfigParser`.

        Args:
            dir_path: The directory to start looking for the INI configuration file.
            file_name: The name of the configuration file to look for.

        Returns:
            None
        """
        # init logging here as this is our most likely entry-point into an idmtools "application"
        from idmtools.core.logging import VERBOSE

        if "IDMTOOLS_CONFIG_FILE" in os.environ:
            if not os.path.exists(os.environ["IDMTOOLS_CONFIG_FILE"]):
                raise FileNotFoundError(f'Cannot for idmtools config at {os.environ["IDMTOOLS_CONFIG_FILE"]}')
            ini_file = os.environ["IDMTOOLS_CONFIG_FILE"]
        else:
            ini_file = cls._find_config(dir_path, file_name)
            # Fallback to user home directories
            if ini_file is None:
                global_config = cls.get_global_configuration_name()
                if os.path.exists(global_config):
                    ini_file = global_config
        if ini_file is None:
            if os.environ.get('IDMTOOLS_NO_CONFIG_WARNING', None) is None:
                # We use print since logger isn't configured unless there is an override(cli)
                print(f"/!\\ WARNING: File '{file_name}' Not Found! For details on how to configure idmtools, see {get_help_version_url('configuration.html')} for details on how to configure idmtools.")
            cls._init_logging()
            return

        cls._config_path = ini_file
        cls._config = ConfigParser()
        cls._config.read(ini_file)

        # in order to have case-insensitive section names, we add the lowercase version of all sections if not present
        sections = cls._config.sections()
        for section in sections:
            lowercase_version = section.lower()
            if not cls._config.has_section(section=lowercase_version):
                cls._config._sections[lowercase_version] = cls._config._sections[section]

        cls._init_logging()
        user_logger.log(VERBOSE, "INI File Used: {}".format(ini_file))

    @classmethod
    def _init_logging(cls):
        from idmtools.core.logging import setup_logging
        # setup logging
        try:
            log_config = cls.get_section('Logging')
            valid_options = ['level', 'log_filename', 'console']
            log_config = {k: v for k, v in log_config.items() if k in valid_options}
        except ValueError:
            log_config = dict(level='INFO', log_filename='idmtools.log', console='off')
        setup_logging(**log_config)

        if platform.system() == "Darwin":
            # see https://bugs.python.org/issue27126
            os.environ['NO_PROXY'] = "*"

        # Do import locally to prevent load error
        from idmtools import __version__
        if "+nightly" in __version__ and os.getenv('IDMTOOLS_HIDE_DEV_WARNING', None) is None:
            user_logger.warning(f"You are using a development version of idmtools, version {__version__}!")

    @classmethod
    @initialization(error=True)
    def get_section(cls, section: str = None, error: bool = True) -> Dict[str, str]:
        """
        Retrieve INI section values (call directly from platform creation).

        Args:
            section: The INI section name where we retrieve all fields.
            error: Should we throw error is we cannot find block

        Returns:
            All fields as a dictionary.

        Raises:
            ValueError: If the block doesn't exist
        """
        if not cls.found_ini():
            return {}

        original_case_section = section
        lower_case_section = section.lower()
        if not cls.has_section(section=lower_case_section) and error:
            raise ValueError(f"Block '{original_case_section}' doesn't exist!")

        section_item = cls._config.items(lower_case_section)
        cls._block = lower_case_section
        return dict(section_item)

    @classmethod
    @initialization(error=False)
    def get_option(cls, section: str = None, option: str = None, force=False, fallback=None) -> str:
        """
        Get configuration value based on the INI section and option.

        Args:
            section: The INI section name.
            option: The INI field name.

        Returns:
            A configuration value as a string.
        """
        if not cls.found_ini():
            return fallback

        if cls._config is None:
            if fallback is None:
                user_logger.warning("No Configuration file defined. Please define a fallback value")
            return fallback

        if section:
            return cls._config.get(section, option, fallback=fallback)
        else:
            return cls._config.get(cls._block, option, fallback=fallback)

    @classmethod
    def ensure_init(cls, dir_path: str = '.', file_name: str = default_config, error: bool = False,
                    force: bool = False) -> None:
        """
        Verify that the INI file loaded and a configparser instance is available.

        Args:
            dir_path: The directory to search for the INI configuration file.
            file_name: The configuration file name to search for.
            force: Force reload of everything
            error: Throws error if idmtools.ini cannot be found

        Returns:
            None

        Raises:
            ValueError: If the config file is found but cannot be parsed
        """
        if force:
            cls.clear_instance()

        if cls._instance is None:
            cls(dir_path, file_name)

        if error and not cls.found_ini():
            raise ValueError("Config file NOT FOUND or IS Empty!")

    @classmethod
    @initialization(error=False)
    def get_config_path(cls) -> str:
        """
        Check which INI configuration file is being used.

        Returns:
            The INI file full path that is loaded.
        """
        return cls._config_path

    @classmethod
    @initialization(error=True)
    def display_config_path(cls) -> None:
        """
        Display the INI file path being used.

        Returns:
            None
        """
        user_logger.info(cls.get_config_path())

    @classmethod
    @initialization(error=True)
    def view_config_file(cls) -> None:
        """
        Display the INI file being used.

        Returns:
            None
        """
        user_logger.info("View Config INI: \n{}".format(cls._config_path))
        user_logger.info('-' * len(cls._config_path), '\n')
        with open(cls._config_path) as f:
            read_data = f.read()
            user_logger.info(read_data)

    @classmethod
    def display_config_block_details(cls, block):
        """
        Display the values of a config block

        Args:
            block: Block to print

        Returns:
            None
        """
        if cls.found_ini():
            from idmtools.core.logging import VERBOSE
            block_details = cls.get_section(block)
            user_logger.log(VERBOSE, f"\n[{block}]")
            user_logger.log(VERBOSE, json.dumps(block_details, indent=3))

    @classmethod
    @initialization(error=False)
    def has_section(cls, section: str) -> bool:
        """
        Does the config contain a section
        Args:
            section:

        Returns:
            True if the section exists, False otherwise
        """
        return cls._config.has_section(section.lower())

    @classmethod
    @initialization
    def has_option(cls, section: str, option: str):
        return cls._config.has_option(section, option, fallback=None)

    @classmethod
    def found_ini(cls) -> bool:
        """
        Did we find the config?

        Returns:
            True if did, False Otherwise
        """
        return cls._config is not None

    @classmethod
    def clear_instance(cls) -> None:
        """
        Uninitialize and clean the :class:`IdmConfigParser` instance.

        Returns:
            None
        """
        cls._config = None
        cls._instance = None
        cls._config_path = None
        cls._block = None
