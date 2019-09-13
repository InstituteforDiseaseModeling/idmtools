import copy
import json
from logging import getLogger
import os
from configparser import ConfigParser
from typing import Dict

default_config = 'idmtools.ini'

# this is the only logger that should not be defined using init_logger
logger = getLogger(__name__)


class IdmConfigParser:
    """
    Parse INI config file
    """
    _config = None
    _instance = None
    _config_path = None

    def __new__(cls, dir_path: str = '.', file_name: str = default_config) -> 'IdmConfigParser':
        """
        Make IdmConfigParser creation as Singleton
        Args:
            dir_path: idmtools INI configuration file directory
            file_name: idmtools INI file name

        Returns: IdmConfigParser instance
        """
        if not cls._instance:
            cls._instance = super(IdmConfigParser, cls).__new__(cls)
            cls._instance._load_config_file(dir_path, file_name)
        return cls._instance

    @classmethod
    def retrieve_settings(cls, section: str = None, field_type: Dict[str, str] = {}) -> Dict[str, str]:
        """
        Called from each Platform. Retrieve INI config values (to be used updating Platform fields)
        Args:
            section: INI section from which to retrieve config values
            field_type: provide pre-requested data types

        Returns: values as a dictionary
        """
        import ast

        cls.ensure_init()

        # retrieve THIS platform config settings
        field_config = cls.get_section(section)

        # update field types
        field_config_updated = copy.deepcopy(field_config)
        fs = set(field_type.keys()).intersection(set(field_config.keys()))

        for fn in fs:
            ft = field_type[fn]
            if ft in (int, float, str):
                field_config_updated[fn] = ft(field_config[fn])
            elif ft is bool:
                field_config_updated[fn] = ast.literal_eval(field_config[fn])

        return field_config_updated

    @classmethod
    def _find_config(cls, dir_path: str = None, file_name: str = default_config) -> None:
        """
        Recursive call to find the INI config file starting from the dir_path provided up to the root,
        stop search once found one
        Args:
            dir_path: directory where we start to look for the idm config file
            file_name: the config file name we will look for

        Returns: None
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
    def _load_config_file(cls, dir_path: str = '.', file_name: str = default_config) -> None:
        """
        Find and then load IDM config file and parse it with configparser
        Args:
            dir_path: directory where we start to look for the idm config file
            file_name: the config file name we will look for

        Returns: None
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
        log_config = cls.get_section('Logging')
        valid_options = ['level', 'log_filename', 'console']
        setup_logging(**{k: v for k, v in log_config.items() if k in valid_options})

    @classmethod
    def get_section(cls, section: str = None) -> Dict[str, str]:
        """
        This is called from platform creation directly and retrieve INI section values
        Args:
            section: INI section name where we retrieve all fields

        Returns: all fields as a dictionary
        """
        cls.ensure_init()
        if cls._config is None:
            return {}

        section_dict = dict(cls._config.items())
        if section not in section_dict:
            print("/!\\ WARNING: Section '{}' Not Found!".format(section))
            return {}

        section = cls._config.items(section)
        return dict(section)

    @classmethod
    def get_block(cls, block_name: str = None) -> Dict[str, str]:
        """
        This is called from platform factoru and retrieve INI section values
        Args:
            block_name: INI section name where we retrieve all fields

        Returns: all fields as a dictionary
        """
        cls.ensure_init()
        if cls._config is None:
            raise ValueError(f"Config file NOT FOUND or IS Empty!")

        section_dict = dict(cls._config.items())
        if block_name not in section_dict:
            raise ValueError(f"Block '{block_name}' doesn't exist!")

        section = cls._config.items(block_name)
        return dict(section)

    @classmethod
    def get_config_path(cls) -> str:
        """
        Check which INI config file we are using
        Returns: the INI file full path we loaded
        """
        cls.ensure_init()
        return cls._config_path

    @classmethod
    def display_config_path(cls) -> None:
        """
        Display the INI file path we are using
        Returns: None
        """
        cls.ensure_init()
        print(cls.get_config_path())

    @classmethod
    def view_config_file(cls) -> None:
        """
        Display the INI file we are using
        Returns: None
        """
        cls.ensure_init()
        if cls._config_path is None:
            return

        print("View Config INI: \n{}".format(cls._config_path))
        print('-' * len(cls._config_path), '\n')
        with open(cls._config_path) as f:
            read_data = f.read()
            print(read_data)

    @classmethod
    def get_option(cls, section: str = None, option: str = None) -> str:
        """
        Get config value based on the INI section and option
        Args:
            section: INI section name
            option: INI field name

        Returns: config value as string
        """
        cls.ensure_init()
        return cls._config.get(section, option)

    @classmethod
    def ensure_init(cls, dir_path: str = '.', file_name: str = default_config) -> None:
        """
        Make sure INI file loaded and configparser instance available
        Args:
            dir_path: directory where we start to look for the idm config file
            file_name: the config file name we will look for

        Returns: None
        """
        if cls._instance is None:
            cls(dir_path, file_name)

    @classmethod
    def display_config_block_details(cls, block):
        if cls._config_path:
            block_details = cls.get_section(block)
            # print('\nConfig_info:')
            print(f"\n[{block}]")
            print(json.dumps(block_details, indent=3))

    @classmethod
    def clear_instance(cls) -> None:
        """
        Works as un_init and make IdmConfigParser clean
        Returns: None
        """
        cls._config = None
        cls._instance = None
        cls._config_path = None
