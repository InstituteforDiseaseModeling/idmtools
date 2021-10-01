"""idmtools FileFilterWorkItem is a interface for SSMT command to act on files using filters in WorkItems.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
import json
import os
from abc import ABC
from os import PathLike
from pathlib import PurePath
from uuid import UUID
import re
import inspect
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from COMPS.Data.CommissionableEntity import CommissionableEntity
from typing import List, Union, Callable, Dict
from idmtools import IdmConfigParser
from idmtools.assets import Asset, AssetCollection
from idmtools.assets.file_list import FileList
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.utils.info import get_help_version_url
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools.core.enums import ItemType, EntityStatus

EntityFilterFunc = Callable[[CommissionableEntity], bool]
FilterableSSMTItem = Union[Experiment, Simulation, IWorkflowItem]
FilenameFormatFunction = Callable[[str], str]
logger = getLogger(__name__)
user_logger = getLogger("user")

WI_PROPERTY_MAP = dict(
    related_experiments=ItemType.EXPERIMENT,
    related_simulations=ItemType.SIMULATION,
    related_work_items=ItemType.WORKFLOW_ITEM,
    related_asset_collections=ItemType.ASSETCOLLECTION
)

# Default list of ignored files
DEFAULT_EXCLUDES = ["StdErr.txt", "StdOut.txt", "WorkOrder.json", "*.log"]


class CrossEnvironmentFilterNotSupport(Exception):
    """Defines cross environment error for when a user tried to filter across multiple comps environments."""
    doc_link: str = "platforms/comps/errors.html#errors"


class AtLeastOneItemToWatch(Exception):
    """Defines error for when there are not items being watched by FileFilterWorkItem."""
    doc_link: str = "platforms/comps/errors.html#errors"


@dataclass(repr=False)
class FileFilterWorkItem(SSMTWorkItem, ABC):
    """
    Defines our filtering workitem base that is used by assetize outputs and download work items.
    """
    #: List of glob patterns. See https://docs.python.org/3.7/library/glob.html for details on the patterns
    file_patterns: List[str] = field(default_factory=list)
    # Exclude patterns.
    exclude_patterns: List[str] = field(default_factory=lambda: copy.copy(DEFAULT_EXCLUDES))
    #: Include Assets directories. This allows patterns to also include items from the assets directory
    include_assets: bool = field(default=False)
    #: Formatting pattern for directory names. Simulations tend to have similar outputs so the workitem puts those in directories using the simulation id by default as the directory name
    simulation_prefix_format_str: str = field(default="{simulation.id}")
    #: WorkFlowItem outputs will not have a folder prefix by default. If you are filtering multiple work items, you may want to set this to "{workflow_item.id}"
    work_item_prefix_format_str: str = field(default=None)
    #: Simulations outputs will not have a folder. Useful when you are filtering a single simulation
    no_simulation_prefix: bool = field(default=False)
    #: Enable verbose
    verbose: bool = field(default=False)
    #: Python Functions that will be ran before Filtering script. The function must be named
    pre_run_functions: List[Callable] = field(default_factory=list)
    #: Python Function to filter entities. This Function should receive a Comps CommissionableEntity. True means include item, false is don't
    entity_filter_function: EntityFilterFunc = field(default=None)
    #: Function to pass a custom function that is called on the name. This can be used to do advanced mapping or renaming of files
    filename_format_function: FilenameFormatFunction = field(default=None)
    #: Enables running jobs without creating executing. It instead produces a file list of what would be includes in the final filter
    dry_run: bool = field(default=False)

    _ssmt_script: str = field(default=None, repr=False)
    # later change to load all functions in file_filter.py
    _ssmt_depends: List[str] = field(default_factory=lambda: ["common.py", "file_filter.py"], repr=False)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        """
        Initialize the FileFilterWorkItem.

        Args:
            item_name: ItemName(Workitem)
            asset_collection_id: Asset collection to attach to workitem
            asset_files: Asset collections files to add
            user_files: User files to add
            command: Command to run

        Returns:
            None

        Raises:
            ValueError - If the ssmt script is not defined.
        """
        if self._ssmt_script is None:
            raise ValueError("When defining a FileFilterWorkItem, you need an _ssmt_script")
        # Set command to nothing here for now. Eventually this will go away after 1.7.0
        self.task = CommandTask(command=f'python3 Assets/{PurePath(self._ssmt_script).name}')
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files, "")

    def create_command(self) -> str:
        """
        Builds our command line for the SSMT Job.

        Returns:
            Command string
        """
        command = f"python3 Assets/{PurePath(self._ssmt_script).name} "
        if self.file_patterns:
            command += '--file-pattern'
            for pattern in self.file_patterns:
                command += f' "{pattern}"'

        if self.exclude_patterns:
            command += ' --exclude-pattern'
            for pattern in self.exclude_patterns:
                command += f' "{pattern}"'

        if self.no_simulation_prefix:
            command += ' --no-simulation-prefix'
        else:
            command += f' --simulation-prefix-format-str "{self.simulation_prefix_format_str}"'

        if self.work_item_prefix_format_str:
            command += f' --work-item-prefix-format-str "{self.work_item_prefix_format_str}"'

        if self.include_assets:
            command += ' --assets'

        for pre_run_func in self.pre_run_functions:
            command += f' --pre-run-func {pre_run_func.__name__}'

        if self.entity_filter_function:
            command += f' --entity-filter-func {self.entity_filter_function.__name__}'

        if self.filename_format_function:
            command += f' --filename-format-func {self.filename_format_function.__name__}'

        if self.verbose:
            command += ' --verbose'

        if self.dry_run:
            command += ' --dry-run'

        command = self._extra_command_args(command)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Command: {command}')

        return command

    def _extra_command_args(self, command: str) -> str:
        """Add extra command arguments."""
        return command

    def __pickle_pre_run(self):
        """
        Pickles the pre run functions.

        Returns:
            None
        """
        if self.pre_run_functions:
            source = ""
            for function in self.pre_run_functions:
                new_source = self.__format_function_source(function)
                source += "\n\n" + new_source
            self.assets.add_or_replace_asset(Asset(filename='pre_run.py', content=source))

    def __pickle_format_func(self):
        """
        Pickle Format filename Function.

        Returns:
            None
        """
        if self.filename_format_function:
            new_source = self.__format_function_source(self.filename_format_function)
            self.assets.add_or_replace_asset(Asset(filename='filename_format_func.py', content=new_source))

    def __pickle_filter_func(self):
        """
        Pickle Filter Function.

        Returns:
            None
        """
        if self.entity_filter_function:
            new_source = self.__format_function_source(self.entity_filter_function)
            self.assets.add_or_replace_asset(Asset(filename='entity_filter_func.py', content=new_source))

    @staticmethod
    def __format_function_source(function: Callable) -> str:
        """
        Formats the function source. Functions could be indented.

        Args:
            function: Function to format

        Returns:
            Formatted function
        """
        source = inspect.getsource(function).splitlines()
        space_base = 0
        while source[0][space_base] == " ":
            space_base += 1
        replace_expr = re.compile("^[ ]{" + str(space_base) + "}")
        new_source = []
        for line in source:
            new_source.append(replace_expr.sub("", line))
        return "\n".join(new_source)

    def clear_exclude_patterns(self):
        """
        Clear Exclude Patterns will remove all current rules.

        Returns:
            None
        """
        self.exclude_patterns = []

    def pre_creation(self, platform: IPlatform) -> None:
        """
        Pre-Creation.

        Args:
            platform: Platform

        Returns:
            None
        """
        self._filter_workitem_pre_creation(platform)
        if self.name is None or self.name == "idmtools workflow item":
            self.name = self.__generate_name()

        current_dir = PurePath(__file__).parent
        # Add our ssm script
        self.assets.add_or_replace_asset(self._ssmt_script)
        utils_dir = current_dir.joinpath("ssmt_utils")
        # Add dependencies
        if self._ssmt_depends:
            for file in self._ssmt_depends:
                self.assets.add_or_replace_asset(utils_dir.joinpath(file))
        self.__pickle_pre_run()
        self.__pickle_format_func()
        self.__pickle_filter_func()
        self.task.command = CommandLine(self.create_command(), is_windows=False)
        if IdmConfigParser.is_output_enabled():
            user_logger.info("Creating Watcher")

        super().pre_creation(platform)

    def _filter_workitem_pre_creation(self, platform):
        """
        Filter the workitem before creation.

        Args:
            platform: Platform

        Returns:
            None

        Raises:
            AtLeastOneItemToWatch - If there are not items we are watching, we cannot run our workitem.
        """
        if self.total_items_watched() == 0:
            raise AtLeastOneItemToWatch("You must specify at least one item to watch")
        if len(self.file_patterns) == 0:
            logger.info("No file pattern specified. Setting to default pattern '**' to filter for all outputs")
            self.file_patterns.append("**")
        self.__convert_ids_to_items(platform)
        self.__ensure_all_dependencies_created_and_in_proper_env(platform)

    def __generate_name(self) -> str:
        """
        Generate Automatic name for the WorkItem.

        Returns:
            Return generated name
        """
        total_items = 0
        name = None
        first_item_type = None
        for prop, item_type in WI_PROPERTY_MAP.items():
            item_type_count = len(getattr(self, prop))
            total_items += len(getattr(self, prop))
            # get first item as we iterate through
            if name is None and item_type_count:
                item = getattr(self, prop)
                name = item[0].id if hasattr(item[0], 'id') else item[0]
                first_item_type = item_type

        if total_items > 1:
            return "Filter outputs"

        return f"Filter outputs for {str(first_item_type).replace('ItemType.', '').lower().capitalize()} {name}"

    def __convert_ids_to_items(self, platform):
        """
        Convert our ids to items.

        Args:
            platform: Platform object

        Returns:
            None
        """
        for prop, item_type in WI_PROPERTY_MAP.items():
            new_items = []
            for item in getattr(self, prop):
                if isinstance(item, (str, PathLike)):
                    # first test if the item is a file
                    if os.path.exists(item):
                        item = platform.get_item_from_id_file(item, item_type)
                    else:
                        if isinstance(item, PathLike):
                            user_logger.warning(f"Could not find a file with name {item}. Attempting to load as an ID")
                        item = platform.get_item(item, item_type, force=True)
                new_items.append(item)
            setattr(self, prop, new_items)

    def __ensure_all_dependencies_created_and_in_proper_env(self, platform: COMPSPlatform):
        """
        Ensures all items we are watching.

        Args:
            platform:

        Returns:
            None

        Raises:
            CrossEnvironmentFilterNotSupport - If items are from multiple environemnts.
        """
        for work_prop, item_type in WI_PROPERTY_MAP.items():
            items = getattr(self, work_prop)
            for item in items:
                if item.status is None:
                    if isinstance(item, IRunnableEntity):
                        item.run(platform=platform)
                    # this should only be sim in this branch
                    elif isinstance(item, Simulation):
                        item.parent.run(platform=platform)
                    elif isinstance(item, AssetCollection):
                        platform.create_items(item)
                if item_type in [ItemType.SIMULATION, ItemType.WORKFLOW_ITEM, ItemType.EXPERIMENT]:
                    fail = False
                    po = item.get_platform_object(platform=platform)
                    if item_type in [ItemType.SIMULATION, ItemType.EXPERIMENT]:
                        if item_type == ItemType.SIMULATION and po.configuration is None or po.configuration.environment_name is None:
                            po = item.parent.get_platform_object(platform=platform)
                        if po.configuration is None:
                            user_logger.warning(f"Cannot determine environment of item of type {item_type} with id of {item.id}. Running filter against items in other environments will result in an error")
                        elif po.configuration.environment_name.lower() != platform.environment.lower():
                            fail = True
                    elif item_type == ItemType.WORKFLOW_ITEM and po.environment_name.lower() != platform.environment.lower():
                        fail = True
                    if fail:
                        raise CrossEnvironmentFilterNotSupport(f"You cannot filter files between environment. In this case, the {item_type.value} {item.id} is in {po.configuration.environment_name} but you are running your workitem in {platform.environment}")

    def total_items_watched(self) -> int:
        """
        Returns the number of items watched.

        Returns:
            Total number of items watched
        """
        total = 0
        for item_type in WI_PROPERTY_MAP.keys():
            total += len(getattr(self, item_type))
        return total

    def run_after_by_id(self, item_id: str, item_type: ItemType, platform: COMPSPlatform = None):
        """
        Runs the workitem after an existing item finishes.

        Args:
            item_id: ItemId
            item_type: ItemType
            platform: Platform

        Returns:
            None

        Raises:
            ValueError - If item_type is not an experiment, simulation, or workflow item
        """
        if item_type not in [ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.WORKFLOW_ITEM]:
            raise ValueError("Currently only Experiment, Simuation, and WorkFlowItems can be filtered")
        p = super()._check_for_platform_from_context(platform)
        extra = dict()
        item = p.get_item(item_id=item_id, item_type=item_type, **extra)
        if item:
            self.from_items(item)
        raise FileNotFoundError(f"Cannot find the item with {item_id} of type {item_type}")

    def from_items(self, item: Union[FilterableSSMTItem, List[FilterableSSMTItem]]):
        """
        Add items to load assets from.

        Args:
            item: Item or list of items to watch.

        Returns:
            None

        Raises:
            ValueError - If any items specified are not an Experiment, Simulation or WorkItem

        Notes:
            We should add suite support in the future if possible. This should be done in client side by converting suite to list of experiments.
        """
        if not isinstance(item, list):
            items_to_add = [item]
        else:
            items_to_add = item
        for i in items_to_add:
            if isinstance(i, Experiment):
                self.related_experiments.append(i)
            elif isinstance(i, Simulation):
                self.related_simulations.append(i)
            elif isinstance(i, IWorkflowItem):
                self.related_work_items.append(i)
            else:
                raise ValueError("We can only filter the output of experiments, simulations, and workitems")

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'COMPSPlatform' = None) -> Union[None]:
        """
        Waits on Filter Workitem to finish. This first waits on any dependent items to finish(Experiment/Simulation/WorkItems).

        Args:
            wait_on_done_progress: When set to true, a progress bar will be shown from the item
            timeout: Timeout for waiting on item. If none, wait will be forever
            refresh_interval: How often to refresh progress
            platform: Platform

        Returns:
            AssetCollection created if item succeeds
        """
        # wait on related items before we wait on our item
        p = super()._check_for_platform_from_context(platform)
        opts = dict(wait_on_done_progress=wait_on_done_progress, timeout=timeout, refresh_interval=refresh_interval, platform=p)
        self._wait_on_children(**opts)

        super().wait(**opts)

    def _wait_on_children(self, **opts):
        """
        Wait on children implementation.

        Loops through the relations and ensure all are done before waiting on ourselve
        Args:
            **opts:

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Wait on items being watched to finish running")
        for item_type in WI_PROPERTY_MAP.keys():
            items = getattr(self, item_type)
            for item in items:
                # The only two done states in idmtools are SUCCEEDED and FAILED
                if item.status not in [EntityStatus.SUCCEEDED, EntityStatus.FAILED]:
                    # We only can wait on Experiments and Workitems. For simulations, we use the parent
                    if isinstance(item, IRunnableEntity):
                        item.wait(**opts)
                    # user simulation's parent to wait
                    elif isinstance(item, Simulation):
                        if item.parent is None:
                            if not item.parent_id:
                                raise ValueError(f"Cannot determine simulation {item.id}'s parent and item still in progress. Please wait on it to complete before {self.__class__.name}")
                            else:
                                item.parent = Experiment.from_id(item.parent_id)
                        item.parent.wait(**opts)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Done waiting on items watching. Now waiting on {self.__class__.name}: {self.id}")
        super().wait(**opts)

    def fetch_error(self, print_error: bool = True) -> Union[Dict]:
        """
        Fetches the error from a WorkItem.

        Args:
            print_error: Should error be printed. If false, error will be returned

        Returns:
            Error info
        """
        if self.status != EntityStatus.FAILED:
            raise ValueError("You cannot fetch error if the items is not in a failed state")

        try:
            file = self.platform.get_files(self, ['error_reason.json'])
            file = file['error_reason.json'].decode('utf-8')
            file = json.loads(file)
            if print_error:
                user_logger.error(f'Error from server: {file["args"][0]}')
                if 'doc_link' in file:
                    user_logger.error(get_help_version_url(file['doc_link']))
                else:
                    user_logger.error(user_logger.error('\n'.join(file['tb'])))
            return file
        except Exception as e:
            logger.exception(e)
