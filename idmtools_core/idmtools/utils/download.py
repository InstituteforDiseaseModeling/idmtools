"""
Provide a command to download files from a platform

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from pathlib import Path
from typing import List, Callable, TYPE_CHECKING, Union

from tqdm import tqdm

from idmtools.core import ItemType, NoPlatformException
from idmtools.utils.filters.asset_filters import default_filter_callback

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.suite import Suite
    from idmtools.entities.experiment import Experiment
    from idmtools.entities.simulation import Simulation
    from idmtools.entities.iworkflow_item import IWorkflowItem
    from idmtools.assets.asset_collection import AssetCollection

FilenameFormatFunction = Callable[[str], str]

DOWNLOAD_PROPERTY_MAP = dict(
    experiments=ItemType.EXPERIMENT,
    simulations=ItemType.SIMULATION,
    work_items=ItemType.WORKFLOW_ITEM,
    suites=ItemType.SUITE,
    asset_collections=ItemType.ASSETCOLLECTION
)

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class DownloadCommand:
    """
    DownloadCommand defines an interface to make downloading and replicating remote experiments locally easy.
    """
    #: List of glob patterns. See https://docs.python.org/3.7/library/glob.html for details on the patterns
    file_patterns: List[str] = field(default_factory=list)
    #: Path to save the downloaded content. Default to the current working directory
    output_path: str = field(default_factory=os.getcwd)
    #: Formatting pattern for directory names for suites
    suite_prefix_format_str: str = field(default="{suite.id}")
    #: Formatting pattern for directory names for experiments
    experiment_prefix_format_str: str = field(default="{experiment.id}")
    #: Formatting pattern for directory names. Simulations tend to have similar outputs so the download command puts those in directories using the simulation id by default as the directory name
    simulation_prefix_format_str: str = field(default="{simulation.id}")
    #: Formatting pattern for directory names. Simulations tend to have similar outputs so the download command puts those in directories using the simulation id by default as the directory name
    asset_collection_prefix_format_str: str = field(default="{asset_collection.id}")
    #: Include Assets directories. This allows patterns to also include items shared assets
    include_assets: bool = field(default=False)
    #: WorkFlowItem outputs will not have a folder prefix by default. If you are filtering multiple work items, you may want to set this to "{workflow_item.id}"
    work_item_prefix_format_str: str = field(default=None)
    #: Simulations outputs will not have a folder. Useful when you are filtering a single simulation
    no_simulation_prefix: bool = field(default=False)
    #: Function to pass a custom function that is called on the name. This can be used to do advanced mapping or renaming of files
    filename_format_function: FilenameFormatFunction = field(default=None)
    #: Enables running jobs without creating executing. It instead produces a file list of what would be includes in the final filter
    dry_run: bool = field(default=False)

    #: Experiments to download
    experiments: list = field(default_factory=list)
    #: Simulations to download
    simulations: list = field(default_factory=list)
    #: Suites to download
    suites: list = field(default_factory=list)
    #: Work-items to download
    work_items: list = field(default_factory=list)
    #: Asset collections to download
    asset_collections: list = field(default_factory=list)

    def __post_init__(self):
        pass

    def __convert_ids_to_items(self, platform):
        """
        Convert our ids to items.

        Args:
            platform: Platform object

        Returns:
            None
        """
        for prop, item_type in DOWNLOAD_PROPERTY_MAP.items():
            new_items = []
            for item in getattr(self, prop):
                if isinstance(item, (str, os.PathLike)):
                    # first test if the item is a file
                    if os.path.exists(item):
                        item = platform.get_item_from_id_file(item, item_type)
                    else:
                        if isinstance(item, os.PathLike):
                            user_logger.warning(f"Could not find a file with name {item}. Attempting to load as an ID")
                        item = platform.get_item(item, item_type, force=True)
                new_items.append(item)
            setattr(self, prop, new_items)

    def __download_simulations(self, base_download_path: Union[str, os.PathLike], simulations: List['Simulation'], executor):
        futures = dict()
        for simulation in simulations:
            if self.simulation_prefix_format_str:
                simulation_output_path = Path(base_download_path).joinpath(self.simulation_prefix_format_str.format(simulation=simulation, experiment=simulation.experiment))
            else:
                simulation_output_path = base_download_path
            self.__download_asset_file_item(executor, futures, simulation, simulation_output_path)
        return futures

    def __download_work_items(self, base_download_path: Union[str, os.PathLike], work_items: List['IWorkflowItem'], executor):
        futures = dict()
        for work_item in work_items:
            if self.work_item_prefix_format_str:
                work_item_output_path = Path(base_download_path).joinpath(self.work_item_prefix_format_str.format(workitem=work_item))
            else:
                work_item_output_path = base_download_path

            self.__download_asset_file_item(executor, futures, work_item, work_item_output_path)
        return futures

    def __download_asset_file_item(self, executor, futures, item: Union['Simulation', 'IWorkflowItem'], output_path):
        if self.include_assets:
            asset_output_path = output_path.joinpath("assets/")
            for asset in item.list_assets(filters=self.file_patterns):
                futures[asset] = executor.submit(asset.download_to_path(asset_output_path))
        for file in item.list_files(filters=self.file_patterns):
            futures[file] = executor.submit(file.download_to_path, output_path)

    def __download_experiments(self, base_download_path: Union[str, os.PathLike], experiments: List['Experiment'], executor, suite: 'Suite' = None):
        futures = dict()
        for experiment in experiments:
            if self.experiment_prefix_format_str:
                experiment_output_path = Path(base_download_path).joinpath(self.experiment_prefix_format_str.format(experiment=experiment, suite=suite))
            else:
                experiment_output_path = base_download_path
            if self.include_assets:
                asset_output_path = experiment_output_path.joinpath("assets/")
                for asset in experiment.list_assets(filters=self.file_patterns):
                    futures[asset] = executor.submit(asset.download_to_path, asset_output_path)
            futures.update(self.__download_simulations(experiment_output_path, experiment.simulations, executor=executor))
        return futures

    def __download_suites(self, executor, suites: List['Suite']):
        futures = dict()
        for suite in suites:
            suite_output_path = Path(self.output_path).joinpath(self.suite_prefix_format_str.format(suite=suite) + "/")
            if self.include_assets:
                asset_output_path = suite_output_path.joinpath("assets/")
                for asset in suite.list_assets(filters=self.file_patterns):
                    futures[asset] = executor.submit(asset.download_to_path, asset_output_path)

            futures.update(self.__download_experiments(suite_output_path, suite.experiments, executor=executor, suite=suite))
        return futures

    def __download_asset_collections(self, base_download_path, executor, asset_collections: List['AssetCollection']):
        futures = dict()
        for ac in asset_collections:
            if self.asset_collection_prefix_format_str:
                ac_output_path = Path(base_download_path).joinpath(self.asset_collection_prefix_format_str.format(asset_collection=ac))
            else:
                ac_output_path = base_download_path

            for asset in ac.list_assets(filters=self.file_patterns):
                futures[asset] = executor.submit(asset.download_to_path, ac_output_path)
        return futures

    def run(self, platform: 'IPlatform' = None):
        if platform is None:
            from idmtools.core.context import get_current_platform
            p = get_current_platform()
            if p is None:
                raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
            platform = p
        self.__convert_ids_to_items(platform)
        for idx, pattern in enumerate(self.file_patterns):
            self.file_patterns[idx] = default_filter_callback(pattern)

        # start with suites, then experiments, then simulations, then asset collections
        download_futures = dict()
        with ThreadPoolExecutor() as executor:
            # start with suites
            download_futures.update(self.__download_suites(executor, self.suites))
            download_futures.update(self.__download_experiments(self.output_path, self.experiments, executor=executor, suite=None))
            download_futures.update(self.__download_simulations(self.output_path, self.simulations, executor=executor))
            download_futures.update(self.__download_work_items(self.output_path, self.work_items, executor=executor))
            download_futures.update(self.__download_asset_collections(self.output_path, executor, self.asset_collections))

            for future in tqdm(iterable=download_futures.values(), total=len(download_futures)):
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Finished {future.short_remote_path()}")
