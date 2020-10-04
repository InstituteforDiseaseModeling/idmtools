import os
from dataclasses import dataclass, field
from logging import getLogger

from functools import partial
from typing import List, Union
from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


AssetizableItem = Union[Experiment, Simulation, IWorkflowItem]
logger = getLogger(__name__)
user_logger = getLogger("user")


@dataclass(repr=False)
class AssetizeOutput(SSMTWorkItem):
    file_patterns: List[str] = field(default_factory=list)
    include_existing_assets: bool = field(default=False)

    def __post_init__(self):
        super().__post_init__()
        self.item_name = "Assetize Output"

    def create_command(self) -> str:
        command = "python3 Assets/assetize_ssmt_script.py "
        for pattern in self.file_patterns:
            command += f'--file-pattern "{pattern}"'
        return command

    def pre_creation(self, platform: IPlatform) -> None:
        super().pre_creation(platform)
        if not self.__are_all_dependencies_created():
            raise ValueError("Ensure all dependent items are in a create state before attempting to create the Assetize Watcher")
        elif self.total_items_watched() == 0:
            raise ValueError("You must specify at least one item to watch")

        if len(self.file_patterns) == 0:
            logger.info("No file pattern specified. Setting to default pattern '**' to assetize all outputs")
            self.file_patterns.append("**")
        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.asset_files.add_file(os.path.join(current_dir, 'assetize_ssmt_script.py'))
        self.command = self.create_command()
        user_logger.info("Creating Watcher")

    def __create_after_other_items_have_been_created(self, item, platform):
        """
        After create the watcher after other items have been created

        Args:
            item: Item that was triggered
            platform: Platform Object

        Returns:
            None
        """
        # Loops through items we are waiting for ids and check if they are not in created state
        all_created = self.__are_all_dependencies_created()
        if all_created:
            # Run without waiting so we just create
            self.run(platform=platform)

    def __are_all_dependencies_created(self) -> bool:
        for item_type in ['related_experiments', 'related_simulations', 'related_work_items']:
            for item in getattr(self, item_type):
                if item.status not in [EntityStatus.CREATED, EntityStatus.RUNNING, EntityStatus.COMMISSIONING, EntityStatus.SUCCEEDED]:
                    return False
        return True

    def total_items_watched(self) -> int:
        total = 0
        for item_type in ['related_experiments', 'related_simulations', 'related_work_items']:
            total += len(getattr(self, item_type))
        return total

    def run_after(self, item: Union[AssetizableItem, List[AssetizableItem]]):
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

            # we call after we know the item has an id
            hook = partial(AssetizeOutput.__create_after_other_items_have_been_created, self)
            i.add_post_creation_hook(hook)
