import copy
import platform
from pathlib import Path
import json
import os
from configparser import ConfigParser
from logging import getLogger, DEBUG
from typing import Any, Dict
from idmtools.core import TRUTHY_VALUES
from idmtools.utils.info import get_help_version_url

default_config = 'idmtools.ini'

# this is the only logger that should not be defined using init_logger
logger = getLogger(__name__)
user_logger = getLogger('user')


def initialization(force=False):
    def wrap(func):
        def wrapped_f(*args, **kwargs):
            IdmConfigParser.ensure_init(force=force)
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
            # Only error when a user overrides the filename for idmtools.ini
            if (dir_path != "." or file_name != default_config) and not cls.found_ini():
                raise ValueError(f"The configuration file {os.path.join(dir_path, file_name)} was not found!")
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
            if os.getenv("IDMTOOLS_NO_CONFIG_WARNING", "F").lower() not in TRUTHY_VALUES:
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
        if IdmConfigParser.get_option("NO_PRINT_CONFIG_USED", fallback="F").lower() not in TRUTHY_VALUES and IdmConfigParser.get_option("SUPPRESS_OUTPUT", fallback="F").lower() not in TRUTHY_VALUES:
            user_logger.log(VERBOSE, "INI File Used: {}".format(ini_file))

    @classmethod
    def _init_logging(cls):
        from idmtools.core.logging import setup_logging
        # set up default log values
        log_config = dict(level='INFO', filename='idmtools.log', console='off', file_level=None)
        # try to fetch options from config file and from environment vars
        for key in log_config.keys():
            value = cls.get_option("logging", key, fallback=None)
            if value is not None:
                log_config[key] = value
        setup_logging(**log_config)

        if platform.system() == "Darwin":
            # see https://bugs.python.org/issue27126
            os.environ['NO_PROXY'] = "*"

        # Do import locally to prevent load error
        from idmtools import __version__
        if "+nightly" in __version__ and os.getenv('IDMTOOLS_HIDE_DEV_WARNING', None) is None:
            user_logger.warning(f"You are using a development version of idmtools, version {__version__}!")

    @classmethod
    @initialization()
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
        original_case_section = section
        lower_case_section = section.lower()
        if (not cls.found_ini() or not cls.has_section(section=lower_case_section)) and error:
            raise ValueError(f"Block '{original_case_section}' doesn't exist!")

        section_item = cls._config.items(lower_case_section)
        cls._block = lower_case_section
        return dict(section_item)

    @classmethod
    @initialization()
    def get_option(cls, section: str = None, option: str = None, fallback=None, environment_first: bool = True) -> str:
        """
        Get configuration value based on the INI section and option.

        Args:
            section: The INI section name.
            option: The INI field name.
            fallback: Fallback value
            environment_first: Try to load from environment var first. Default to True. Environment variable names are in form IDMTOOLS_SECTION_OPTION

        Returns:
            A configuration value as a string.
        """
        if environment_first:
            evn_name = "_".join(filter(None, ["IDMTOOLS", section, option])).upper()
            value = os.environ.get(evn_name, None)
            if value:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Loaded option from environment var {evn_name}")
                return value
        if not cls.found_ini():
            return fallback

        if cls._config is None:
            if fallback is None:
                user_logger.warning("No Configuration file defined. Please define a fallback value")
            return fallback

        if section:
            return cls._config.get(section, option, fallback=fallback)
        else:
            return cls._config.get("COMMON", option, fallback=fallback)

    @classmethod
    def is_progress_bar_disabled(cls) -> bool:
        """
        Are progress bars disabled

        Returns:
            Return is progress bars should be enabled
        """
        return all([x.lower() in TRUTHY_VALUES for x in [IdmConfigParser.get_option(None, "DISABLE_PROGRESS_BAR", 'f')]])

    @classmethod
    def ensure_init(cls, dir_path: str = '.', file_name: str = default_config, force: bool = False) -> None:
        """
        Verify that the INI file loaded and a configparser instance is available.

        Args:
            dir_path: The directory to search for the INI configuration file.
            file_name: The configuration file name to search for.
            force: Force reload of everything

        Returns:
            None

        Raises:
            ValueError: If the config file is found but cannot be parsed
        """
        if force:
            cls.clear_instance()

        if cls._instance is None:
            cls(dir_path, file_name)

    @classmethod
    @initialization()
    def get_config_path(cls) -> str:
        """
        Check which INI configuration file is being used.

        Returns:
            The INI file full path that is loaded.
        """
        return cls._config_path

    @classmethod
    @initialization()
    def display_config_path(cls) -> None:
        """
        Display the INI file path being used.

        Returns:
            None
        """
        user_logger.info(cls.get_config_path())

    @classmethod
    @initialization()
    def view_config_file(cls) -> None:
        """
        Display the INI file being used.

        Returns:
            None
        """
        if cls._config_path is None:
            user_logger.warning("No configuration fouind")
        else:
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
    @initialization()
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
