"""
This is FilePlatform operations utils.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import os
from pathlib import Path
from logging import getLogger
from typing import Dict, Union, List, Optional

from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import Suite
from idmtools.core import EntityStatus, ItemType
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation

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

    _metas: Dict
    _platform_directory: str

    def __init__(self, metas: Dict):
        """
        Constructor.
        Args:
            metas: metadata
        """
        self._metas = metas
        self._platform_directory = metas["dir"]

    def get_platform_object(self):
        """
        Get platform.

        Returns:
            Platform
        """
        return self


class FileSuite(FileItem, Suite):
    """
    Represents a Suite loaded from a file platform.
    """
    def __init__(self, metas: Dict):
        """
        Initialize a FileSuite object from metadata.

        This constructor extracts common suite metadata such as ID, name, status, experiments,
        and tags from a given metadata dictionary.
        Args:
            metas (Dict): A dictionary containing suite metadata. Expected keys:
                      - 'id': Unique identifier for the suite.
                      - 'name': Name of the suite.
                      - 'status': Execution status.
                      - 'experiments': List of experiment IDs or IEntity instances.
                      - 'tags': Dictionary of metadata tags.
        """
        FileItem.__init__(self, metas)
        self.uid = metas['id']
        self.name = metas['name']
        self.status = metas['status']
        self.__experiments: Optional[List[str, IEntity]] = metas['experiments']
        self.tags = metas['tags']

    @property
    def experiments(self) -> List:
        """
        Retrieve the list of experiments associated with this suite.
        Returns:
            List: A list of resolved `Experiment` objects.
        """
        return self.get_experiments()

    def get_experiments(self) -> List:
        """
        Resolve and return the list of experiments.

        For any unresolved entries (e.g., experiment IDs), this method uses
        the current platform to retrieve the full `Experiment` object. Already
        resolved `Experiment` instances are returned as-is.

        Returns:
            List: A list of `Experiment` objects resolved from the internal metadata.
        """
        platform = self.get_current_platform_or_error()
        exp_list = []
        for exp in self.__experiments:
            if isinstance(exp, Experiment):
                exp_list.append(exp)
            else:
                exp_list.append(platform.get_item(exp, item_type=ItemType.EXPERIMENT, force=True, raw=True))
        self.__experiments = exp_list
        return exp_list

    @experiments.setter
    def experiments(self, experiments: List):
        """
        Set the list of experiments for this suite.

        Accepts either resolved `Experiment` objects or a mix of IDs and objects.
        The list will be resolved to full objects upon next access(get_experiments()).

        Args:
            experiments (List): A list of experiment IDs or `Experiment` instances.
        """
        self.__experiments = experiments

    def __repr__(self):
        """
        String representation of suite.
        """
        return f"<{self.__class__.__name__} {self.uid} - {len(self.experiments)} experiments>"

    def add_experiment(self, experiment: 'Experiment') -> 'NoReturn':  # noqa: F821
        """
        Add an experiment to the suite.

        Args:
            experiment: the experiment to be linked to suite
        """
        self.__experiments.append(experiment)


class FileExperiment(FileItem, Experiment):
    """
    Represents an Experiment loaded from a file platform.

    This subclass of `Experiment` maps metadata into a lightweight experiment representation,
    where simulations may initially be stored as either IDs or resolved `Simulation` objects.
    """
    def __init__(self, metas: Dict):
        """
        Initialize a FileExperiment from a metadata dictionary.

        Args:
            metas (Dict): Metadata dictionary containing keys:
                - 'id': Unique identifier for the experiment.
                - 'name': Experiment name.
                - 'status': Status of the experiment (raw value).
                - 'suite_id': ID of the parent suite.
                - 'simulations': List of simulation IDs or `Simulation` objects.
                - 'tags': Dictionary of experiment tags.
                - 'assets': Asset collection or related metadata.
        """
        FileItem.__init__(self, metas)
        self.suite_id = self.parent_id = metas['suite_id']
        self.__simulations: Optional[List[str, IEntity]] = metas['simulations']
        self.uid = metas['id']
        self.name = metas['name']
        self._status = metas['status']
        self.tags = metas['tags']
        self.assets = metas['assets']

    @property
    def simulations(self) -> List:
        """
        Access the list of simulations associated with the experiment.

        Returns:
            List: A list containing either simulation IDs or resolved `Simulation` objects.
        """
        return self.get_simulations()

    def get_simulations(self) -> List:
        """
        Resolve and return full `Simulation` objects from their IDs.

        This method uses file platform to retrieve any simulations
        that are not yet resolved, and replaces unresolved IDs in-place.

        Returns:
            List: Fully resolved list of `Simulation` objects.
        """
        platform = self.get_current_platform_or_error()
        sim_list = []
        for sim in self.__simulations:
            if isinstance(sim, Simulation):
                sim_list.append(sim)
            else:
                sim_list.append(platform.get_item(sim, item_type=ItemType.SIMULATION, force=True, raw=True))
        self.__simulations = sim_list
        return sim_list

    @simulations.setter
    def simulations(self, simulations: List):
        """
        Set the simulations list directly.

        Args:
            simulations (List): A list of simulation IDs or `Simulation` instances.
        """
        self.__simulations = simulations

    def add_simulation(self, simulation: 'Simulation') -> 'NoReturn':  # noqa: F821
        """
        Add a single simulation to the experiment.

        Args:
            simulation (Simulation): The simulation to add.
        """
        self.__simulations.append(simulation)

    @property
    def status(self):
        """
        Get status.
        Returns:
            Status
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Set Status.
        Args:
            status: status

        Returns:
            None
        """
        self._status = status

    def __repr__(self):
        """
        String representation of experiment.
        """
        return f"<{self.__class__.__name__} {self.uid} - {len(self.simulations)} simulations>"


class FileSimulation(FileItem, Simulation):
    """
    Represents a simulation loaded from file metadata.

    This class is a lightweight wrapper around the standard `Simulation` object,
    used by the FilePlatform. It initializes the simulation using values from
    a metadata dictionary, typically derived from file contents.

    Attributes:
        uid (str): uid of simulation.
        parent_id (str): ID of the parent experiment.
        experiment_id (str): Alias of `parent_id` for clarity.
        name (str): Name of the simulation.
        status (EntityStatus or raw value): Execution status.
        tags (Dict): Key-value metadata tags.
        task (Any): Task definition or reference (platform-dependent).
        assets (Any): Asset metadata or collection.
    """
    def __init__(self, metas: Dict):
        """
        Constructor.
        Args:
            metas: Metas dict
        """
        FileItem.__init__(self, metas)
        self.uid = metas['id']
        self.parent_id = metas['parent_id']
        self.experiment_id = metas['parent_id']
        self.name = metas['name']
        self.status = metas['status']
        self.tags = metas['tags']
        self.task = metas['task']
        self.assets = metas['assets']


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
    if tags is None:
        tags = {}
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


def validate_folder_files_path_length(common_asset_dir: Union[Path, str], link_dir: Union[Path, str],
                                      limit: int = 256):
    """
    Validate common asset path length.
    Args:
        common_asset_dir: common asset directory
        link_dir: link directory
        limit: path length limit
    Returns:
        None
    """
    if not is_windows():
        return
    if is_long_paths_enabled():
        return
    asset_path = get_max_filepath(common_asset_dir)
    if asset_path is None:
        validate_file_path_length(link_dir, limit)
    else:
        sim_asset_path = os.path.join(str(link_dir), asset_path)
        validate_file_path_length(sim_asset_path, limit)


def validate_file_copy_path_length(src: Union[Path, str], dest: Union[Path, str], limit: int = 256):
    """
    Validate file copy path length.
    Args:
        src: source path
        dest: destination path
        limit: path length limit
    Returns:
        None
    """
    if not is_windows():
        return
    if is_long_paths_enabled():
        return
    filename = Path(src).name
    dest_file = Path(dest, filename)
    validate_file_path_length(dest_file, limit)


def validate_file_path_length(file_path: Union[Path, str], limit: int = 256):
    """
    Validate file path length.
    Args:
        file_path: file path
        limit: path length limit
    Returns:
        None
    """
    if not is_windows():
        return
    if is_long_paths_enabled():
        return
    total_length = len(str(file_path))
    if total_length > limit:
        user_logger.warning(
            f"\nFile path length too long: {total_length} > {limit}. Refer to file: '{file_path}'")
        user_logger.warning(
            "You may want to adjust your job_directory location, short Experiment name or Suite name to reduce the file path length. Or you can enable long paths in Windows, refer to https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/The-Windows-10-default-path-length-limitation-MAX-PATH-is-256-characters.html.")
        # raise FileNotFoundError(f"File path length too long: {total_length} > {limit}. Refer to file: '{file_path}'")
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
    import winreg
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
        return
