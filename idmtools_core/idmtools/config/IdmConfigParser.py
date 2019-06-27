import copy
import os
from configparser import ConfigParser
from typing import Dict

default_config = 'idmtools.ini'


class IdmConfigParser:
    """
    Parse INI file
    """
    _config = None
    _instance = None
    _config_path = None

    def __new__(cls, dir_path: str = '.', file_name: str = default_config) -> 'IdmConfigParser':
        """

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
        import ast

        cls.ensure_init()

        # retrieve THIS platform config settings
        field_config = cls._get_section(section)

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
        ini_file = cls._find_config(dir_path, file_name)
        if ini_file is None:
            print("/!\\ WARNING: File '{}' Not Found!".format(file_name))
            return

        print("INI File Used: {}\n".format(ini_file))

        cls._config = ConfigParser()
        cls._config.read(ini_file)

    @classmethod
    def _get_section(cls, section: str = None) -> Dict[str, str]:
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
    def get_config_path(cls) -> str:
        cls.ensure_init()
        return cls._config_path

    @classmethod
    def display_config_path(cls) -> None:
        cls.ensure_init()
        print(cls.get_config_path())

    @classmethod
    def view_config_file(cls) -> None:
        cls.ensure_init()
        print("View Config INI: \n{}".format(cls._config_path))
        print('-' * len(cls._config_path), '\n')
        with open(cls._config_path) as f:
            read_data = f.read()
            print(read_data)

    @classmethod
    def get_option(cls, section: str = None, option: str = None):
        cls.ensure_init()
        return cls._config.get(section.upper(), option)

    @classmethod
    def ensure_init(cls, dir_path: str = '.', file_name: str = default_config):
        if cls._instance is None:
            cls(dir_path, file_name)
