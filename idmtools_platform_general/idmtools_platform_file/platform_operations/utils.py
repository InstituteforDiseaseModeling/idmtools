"""
This is FilePlatform operations utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import winreg
from pathlib import Path
from logging import getLogger
from typing import Dict, Union
from idmtools.entities import Suite
from idmtools.core import ItemType, EntityStatus
from idmtools.entities.experiment import Experiment

logger = getLogger(__name__)
user_logger = getLogger("user")

FILE_MAPS = {
    "0": EntityStatus.SUCCEEDED,
    "-1": EntityStatus.FAILED,
    "100": EntityStatus.RUNNING,
    "None": EntityStatus.CREATED
}


class FileItem:
    """
    Represent File Object.
    """

    def __init__(self, metas: Dict):
        """
        Constructor.
        Args:
            metas: metadata
        """
        for key, value in metas.items():
            setattr(self, key, value)

    def get_platform_object(self):
        """
        Get platform.

        Returns:
            Platform
        """
        return self


class FileSuite(FileItem):
    """
    Represent File Suite.
    """

    def __init__(self, metas: Dict):
        """
        Constructor.
        Args:
            metas: metadata
        """
        super().__init__(metas)
        self.item_type = ItemType.SUITE


class FileExperiment(FileItem):
    """
    Represent File Experiment.
    """

    def __init__(self, metas: Dict):
        """
        Constructor.
        Args:
            metas: metadata
        """
        super().__init__(metas)
        self.item_type = ItemType.EXPERIMENT


class FileSimulation(FileItem):
    """
    Represent File Simulation.
    """

    def __init__(self, metas: Dict):
        """
        Constructor.
        Args:
            metas: metadata
        """
        super().__init__(metas)
        self.item_type = ItemType.SIMULATION


def clean_experiment_name(experiment_name: str) -> str:
    """
    Handle some special characters in experiment names.
    Args:
        experiment_name: name of the experiment
    Returns:
        the experiment name allowed for use
    """
    import re
    chars_to_replace = ['/', '\\', ':', "'", '"', '?', '<', '>', '*', '|', "\0", "(", ")", "[", "]", '`', ',', '!', '$',
                        '&', '"', ' ']
    clean_names_expr = re.compile(f'[{re.escape("".join(chars_to_replace))}]')

    experiment_name = clean_names_expr.sub("_", experiment_name)
    return experiment_name.encode("ascii", "ignore").decode('utf8').strip()


def add_dummy_suite(experiment: Experiment, suite_name: str = None, tags: Dict = None) -> Suite:
    """
    Create Suite parent for given experiment.
    Args:
        experiment: idmtools Experiment
        suite_name: new Suite name
        tags: new Suite tags
    Returns:
        Suite
    """
    if suite_name is None:
        suite_name = 'Suite'
    suite = Suite(name=suite_name)

    if not tags:
        suite.tags = tags

    # add experiment
    suite.add_experiment(experiment)

    return suite


def get_max_filepath(dir_path: Union[Path, str]) -> str:
    """
    Get the maximum file path in a directory.
    Args:
        dir_path: directory path

    Returns:
        maximum file relative path
    """
    max_length = 0  # Variable to store the maximum filename length
    max_file_path = None  # Variable to store the maximum relative filepath

    # Walk through all files and subdirectories recursively
    dir_path = os.path.abspath(dir_path)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            full_path = os.path.join(root, file)
            file_path = full_path.replace(dir_path, '').lstrip('\\')
            if max_file_path is None:
                max_file_path = file_path
                max_length = len(max_file_path)
            else:
                max_length_new = max(max_length, len(file_path))
                if max_length_new > max_length:
                    max_file_path = file_path
                    max_length = len(max_file_path)

    return max_file_path


def validate_common_assets_path_length(common_asset_dir: Union[Path, str], link_dir: Union[Path, str],
                                       limit: int = 256):
    """
    Validate common asset path length.
    Args:
        common_asset_dir: common asset directory
        link_dir: link directory
    Returns:
        None
    """
    if is_long_paths_enabled():
        return
    asset_path = get_max_filepath(common_asset_dir)
    sim_asset_path = os.path.join(str(link_dir), asset_path)
    total_length = len(str(sim_asset_path))
    if total_length > limit:
        user_logger.warning(
            f"\nSome file has path length too long: {total_length} > {limit}. For example, '{sim_asset_path}'")
        user_logger.warning(
            "You may want to adjust your job_directory to reduce the file path length. Or you can enable long paths in Windows, refer to https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html.")
        exit(-1)


def is_windows() -> bool:
    """
    Check if the platform is Windows.
    Returns:
        True if Windows, False otherwise
    """
    # return os.name == 'nt'
    import platform
    return platform.system() in ["Windows"]


def is_long_paths_enabled() -> bool:
    """Check if long paths are enabled in Windows."""
    try:
        # Open the registry key where LongPathsEnabled is stored
        registry_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0,
            winreg.KEY_READ
        )
        # Query the value of LongPathsEnabled
        long_paths_enabled, _ = winreg.QueryValueEx(registry_key, "LongPathsEnabled")
        winreg.CloseKey(registry_key)

        # Return True if it's enabled (i.e., value is 1), otherwise False
        return long_paths_enabled == 1
    except FileNotFoundError:
        # The registry key or value does not exist
        return False
    except Exception as e:
        print(f"Error checking long paths: {e}")
        return False
