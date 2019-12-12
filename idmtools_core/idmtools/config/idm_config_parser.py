import os
import copy
import json
from logging import getLogger
from configparser import ConfigParser
from typing import Dict, Any

default_config = 'idmtools.ini'

# this is the only logger that should not be defined using init_logger
logger = getLogger(__name__)


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
    def retrieve_settings(cls, section: str = None, field_type: Dict[str, str] = {}) -> Dict[str, str]:
        """
        Retrieve INI configuration values (to be used when updating platform fields). Call from each platform.

        Args:
            section: The INI section from which to retrieve configuration values.
            field_type: The requested data types.

        Returns:
            The configuration values as a dictionary.
        """
        import ast

        cls.ensure_init()

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
        # init logging here as this is our most likely entry-point into an idm-tools "application"
        from idmtools.core.logging import setup_logging

        ini_file = cls._find_config(dir_path, file_name)
        if ini_file is None:
            print("/!\\ WARNING: File '{}' Not Found!".format(file_name))
            return

        print("INI File Used: {}".format(ini_file))

        cls._config = ConfigParser()
        cls._config.read(ini_file)

        # setup logging
        log_config = cls.get_section('Logging')
        valid_options = ['level', 'log_filename', 'console']
        setup_logging(**{k: v for k, v in log_config.items() if k in valid_options})

    @classmethod
    def get_section(cls, section: str = None, force=False) -> Dict[str, str]:
        """
        Retrieve INI section values (call directly from platform creation).

        Args:
            section: The INI section name where we retrieve all fields.

        Returns:
            All fields as a dictionary.
        """
        cls.ensure_init(force=force)
        if not cls.found_ini():
            return {}

        block_name = section
        if not cls.has_section(block_name):
            if force:
                raise ValueError(f"Block '{block_name}' doesn't exist!")
            else:
                print("/!\\ WARNING: Section '{}' Not Found!".format(block_name))
                return {}

        section = cls._config.items(block_name)
        cls._block = block_name
        return dict(section)

    @classmethod
    def get_block(cls, block_name: str = None) -> Dict[str, str]:
        """
        Call from platform factory and retrieve INI section values.

        Args:
            block_name: The INI section name where we retrieve all fields.

        Returns:
            All fields as a dictionary.
        """
        cls.ensure_init(force=True)
        if not cls.has_section(block_name):
            raise ValueError(f"Block '{block_name}' doesn't exist!")

        section = cls._config.items(block_name)
        cls._block = block_name
        return dict(section)

    @classmethod
    def get_option(cls, section: str = None, option: str = None, force=False) -> str:
        """
        Get configuration value based on the INI section and option.

        Args:
            section: The INI section name.
            option: The INI field name.

        Returns:
            A configuration value as a string.
        """
        cls.ensure_init(force=force)
        if not cls.found_ini():
            return None

        if section:
            return cls._config.get(section, option, fallback=None)
        else:
            return cls._config.get(cls._block, option, fallback=None)

    @classmethod
    def ensure_init(cls, dir_path: str = '.', file_name: str = default_config, force=False) -> None:
        """
        Verify that the INI file loaded and a configparser instance is available.

        Args:
            dir_path: The directory to search for the INI configuration file.
            file_name: The configuration file name to search for.

        Returns:
            None
        """
        if cls._instance is None:
            cls(dir_path, file_name)

        if force and not cls.found_ini():
            raise ValueError(f"Config file NOT FOUND or IS Empty!")

    @classmethod
    def get_config_path(cls) -> str:
        """
        Check which INI configuration file is being used.

        Returns:
            The INI file full path that is loaded.
        """
        cls.ensure_init()
        return cls._config_path

    @classmethod
    def display_config_path(cls) -> None:
        """
        Display the INI file path being used.

        Returns:
            None
        """
        cls.ensure_init(force=True)
        print(cls.get_config_path())

    @classmethod
    def view_config_file(cls) -> None:
        """
        Display the INI file being used.

        Returns:
            None
        """
        cls.ensure_init(force=True)
        print("View Config INI: \n{}".format(cls._config_path))
        print('-' * len(cls._config_path), '\n')
        with open(cls._config_path) as f:
            read_data = f.read()
            print(read_data)

    @classmethod
    def display_config_block_details(cls, block):
        if cls.found_ini():
            block_details = cls.get_section(block)
            # print('\nConfig_info:')
            print(f"\n[{block}]")
            print(json.dumps(block_details, indent=3))

    @classmethod
    def has_section(cls, section):
        cls.ensure_init()
        return cls._config.has_section(section)

    @classmethod
    def has_option(cls, section, option):
        cls.ensure_init()
        return cls._config.has_option(section, option, fallback=None)

    @classmethod
    def found_ini(cls):
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
