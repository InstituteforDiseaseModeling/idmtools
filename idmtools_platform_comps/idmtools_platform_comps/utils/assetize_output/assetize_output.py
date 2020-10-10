from uuid import UUID

import re
import inspect
import os
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from COMPS.Data.CommissionableEntity import CommissionableEntity
from typing import List, Union, Callable, Dict
from idmtools.assets import Asset, AssetCollection
from idmtools.assets.file_list import FileList
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.relation_type import RelationType
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
from idmtools.core.enums import ItemType, EntityStatus

EntityFilterFunc = Callable[[CommissionableEntity], bool]
AssetizableItem = Union[Experiment, Simulation, IWorkflowItem]
logger = getLogger(__name__)
user_logger = getLogger("user")

WI_PROPERTY_MAP = dict(
    related_experiments=ItemType.EXPERIMENT,
    related_simulations=ItemType.SIMULATION,
    related_work_items=ItemType.WORKFLOW_ITEM,
    related_asset_collections=ItemType.ASSETCOLLECTION
)


@dataclass(repr=False)
class AssetizeOutput(SSMTWorkItem):
    #: List of glob patterns. See https://docs.python.org/3.7/library/glob.html for details on the patterns
    file_patterns: List[str] = field(default_factory=list)
    # Exclude patterns.
    exclude_patterns: List[str] = field(default_factory=lambda: ["StdErr.txt", "StdOut.txt", "WorkOrder.json", "*.log"])
    #: Include Assets directories. This allows patterns to also include items from the assets directory
    include_assets: bool = field(default=False)
    #: Formatting pattern for directory names. Simulations tend to have similar outputs so Assetize puts those in directories using the simulation id by default as the directory name
    simulation_prefix_format_str: str = field(default="{simulation.id}")
    #: WorkFlowItem outputs will not have a folder prefix by default. If you are assetizing multiple work items, you may want to set this to "{workflow_item.id}"
    work_item_prefix_format_str: str = field(default=None)
    #: Simulations outputs will not have a folder. Useful when you are assetizing a single simulation
    no_simulation_prefix: bool = field(default=False)
    #: Enable verbose
    verbose: bool = field(default=False)
    #: Python Functions that will be ran before Assetizing script. The function must be named
    pre_run_functions: List[Callable] = field(default_factory=list)
    #: Python Function to filter entities. This Function should receive a Comps CommissionableEntity. Return True if item should be assetize, False otherwise
    entity_filter_function: EntityFilterFunc = field(default=None)
    # Dictionary of tags to apply to the results asset collection
    asset_tags: Dict[str, str] = field(default_factory=dict)
    #: The asset collection created by Assetize
    asset_collection: AssetCollection = field(default=None)
    dry_run: bool = field(default=False)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        # Set command to nothing here for now. Eventually this will go away after 1.7.0
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files, command='assetize_ssmt_script.py')
        # we need all our items as true entities, so convert them to entities

    def create_command(self) -> str:
        """
        Builds our command line for the SSMT Job

        Returns:
            Command string
        """
        command = "python3 Assets/assetize_ssmt_script.py "
        for pattern in self.file_patterns:
            command += f'--file-pattern "{pattern}"'

        for pattern in self.exclude_patterns:
            command += f' --exclude-pattern "{pattern}"'

        for name, value in self.asset_tags.items():
            command += f' --asset-tag "{name}={value}"'

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

        if self.verbose:
            command += ' --verbose'

        if self.dry_run:
            command += ' --dry-run'

        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Command: {command}')

        return command

    def __pickle_pre_run(self):
        """
        Pickles the pre run functions

        Returns:

        """
        if self.pre_run_functions:
            source = ""
            for function in self.pre_run_functions:
                new_source = self.__format_function_source(function)
                source += "\n\n" + new_source
            self.assets.add_or_replace_asset(Asset(filename='pre_run.py', content=source))

    def __pickle_filter_func(self):
        """
        Pickle Filter Function

        Returns:

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
        Pre-Creation

        Args:
            platform: Platform

        Returns:

        """
        super().pre_creation(platform)

        if self.name is None:
            self.name = self.__generate_name()

        self.__convert_ids_to_items(platform)
        self.__ensure_all_dependencies_created(platform)

        if len(self.asset_tags) == 0:
            self.__generate_tags()
        if self.total_items_watched() == 0:
            raise ValueError("You must specify at least one item to watch")

        if len(self.file_patterns) == 0:
            logger.info("No file pattern specified. Setting to default pattern '**' to assetize all outputs")
            self.file_patterns.append("**")
        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.assets.add_or_replace_asset(os.path.join(current_dir, 'assetize_ssmt_script.py'))
        self.__pickle_pre_run()
        self.__pickle_filter_func()
        self.task.command = self.create_command()
        user_logger.info("Creating Watcher")

    def __generate_tags(self):
        """
        Add the defaults tags to the WorkItem

        Returns:
            None
        """
        for experiment in self.related_experiments:
            self.asset_tags['AssetizedOutputfromFromExperiment'] = str(experiment.id)
        for simulation in self.related_simulations:
            self.asset_tags['AssetizedOutputfromFromSimulation'] = str(simulation.id)
        for work_item in self.related_work_items:
            self.asset_tags['AssetizedOutputfromFromWorkItem'] = str(work_item.id)
        for ac in self.related_asset_collections:
            self.asset_tags['AssetizedOutputfromAssetCollection'] = str(ac.id)

    def __generate_name(self) -> str:
        """
        Generate Automatic name for the WorkItem

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
            return "Assetize outputs"

        return f"Assetize outputs for {str(first_item_type).replace('ItemType.', '').lower().capitalize()} {name}"

    def __convert_ids_to_items(self, platform):
        """
        Convert our ids to items

        Args:
            platform: Platform object

        Returns:
            None
        """

        for prop, item_type in WI_PROPERTY_MAP.items():
            new_items = []
            for id in getattr(self, prop):
                if isinstance(id, str):
                    new_items.append(platform.get_item(id, item_type))
                else:
                    new_items.append(id)
            setattr(self, prop, new_items)

    def __ensure_all_dependencies_created(self, platform: IPlatform):
        """
        Ensures all items we are watching
        Args:
            platform:

        Returns:

        """
        for item_type in WI_PROPERTY_MAP.keys():
            items = getattr(self, item_type)
            for item in items:
                if item.status is None:
                    if isinstance(item, IRunnableEntity):
                        item.run(platform=platform)
                    # this should only be sim in this branch
                    elif isinstance(item, Simulation):
                        item.parent.run(platform=platform)
                    elif isinstance(item, AssetCollection):
                        platform.create_items(item)

    def total_items_watched(self) -> int:
        """
        Returns the number of items watched

        Returns:
            Total number of items watched
        """
        total = 0
        for item_type in WI_PROPERTY_MAP.keys():
            total += len(getattr(self, item_type))
        return total

    def run_after_by_id(self, item_id: str, item_type: ItemType, platform: IPlatform = None):
        if item_type not in [ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.WORKFLOW_ITEM]:
            raise ValueError("Currently only Experiment, Simuation, and WorktforlItems can be assetize")
        p = super()._check_for_platform_from_context(platform)
        item = p.get_item(item_id=item_id, item_type=item_type)
        if item:
            self.from_items(item)
        raise FileNotFoundError(f"Cannot find the item with {item_id} of type {item_type}")

    def from_items(self, item: Union[AssetizableItem, List[AssetizableItem]]):
        """
        Add items to load assets from

        Args:
            item: Item or list of items to watch.

        Returns:

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
                raise ValueError("We can only assetize the output of experiments, simulations, and workitems")

    def run(self, wait_until_done: bool = False, platform: 'IPlatform' = None, wait_on_done_progress: bool = True, wait_on_done: bool = True, **run_opts) -> Union[AssetCollection, None]:
        """
        Run the AssetizeOutput

        Args:
            wait_until_done: Wait until Done will wait for the workitem to complet
            platform: Platform Object
            wait_on_done_progress: When set to true, a progress bar will be shown from the item
            wait_on_done: Wait for item to be done. This will first wait on any dependencies
            **run_opts: Additional options to pass to Run on platform

        Returns:
            AssetCollection created if item succeeds
        """
        p = super()._check_for_platform_from_context(platform)
        p.run_items(self, wait_on_done_progress=wait_on_done_progress, **run_opts)
        if wait_until_done or wait_on_done:
            return self.wait(wait_on_done_progress=wait_on_done_progress, platform=p)

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None) -> Union[AssetCollection, None]:
        """
        Waits on Assetize Workitem to finish. This first waits on any dependent items to finish(Experiment/Simulation/WorkItems)

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
        self.__wait_on_children(**opts)

        super().wait(**opts)
        if self.status == EntityStatus.SUCCEEDED:
            # If we succeeded, get our AC
            comps_workitem = self.get_platform_object(force=True)
            acs = comps_workitem.get_related_asset_collections(RelationType.Created)
            if acs:
                self.asset_collection = AssetCollection.from_id(acs[0].id, platform=p)
                return self.asset_collection

    def __wait_on_children(self, **opts):
        """
        Wait on children implementation

        Loops through the relations and ensure all are done before waiting on ourselve
        Args:
            **opts:

        Returns:

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
                            if item.parent_id:
                                item.parent = Experiment.from_id(item.parent_id)
                            else:
                                raise ValueError(f"Cannot determine simulation {item.id}'s parent and item still in progress. Please wait on it to complete before AssetizingOutputs")
                        item.parent.wait(**opts)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Done waiting on items watching. Now waiting on Assetize Outputs: {self.id}")
        super().wait(**opts)
