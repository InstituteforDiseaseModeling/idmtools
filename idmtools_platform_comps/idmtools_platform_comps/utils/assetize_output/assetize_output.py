from dataclasses import dataclass, field
from functools import partial
from typing import List, Union
from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


AssetizableItem = Union[Experiment, Simulation, IWorkflowItem]

@dataclass(repr=False)
class AssetizeOutput(SSMTWorkItem):
    file_patterns: List[str] = field(default=list)

    def __post_init__(self):
        super().__post_init__()

    def create_command(self) -> str:
        command = "python3 assetize_output.py "
        for experiment in self.related_experiments:
            command += f"--experiment {experiment.id} "

        for simulation in self.related_simulations:
            command += f"--simulation {simulation.id} "

        for wi in self.related_work_items:
            command += f"--work-item {wi.id} "

        return command

    def pre_creation(self, platform: IPlatform) -> None:
        super().pre_creation(platform)
        if not self.__are_all_dependencies_created():
            raise ValueError("Ensure all dependent items are in a create state before attempting to create the Assetize Watcher")

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
            for items in getattr(self, item_type):
                for item in items:
                    if item.status not in [EntityStatus.CREATED, EntityStatus.RUNNING, EntityStatus.COMMISSIONING, EntityStatus.SUCCEEDED]:
                        return False
        return True

    def run_after(self, item: Union[AssetizableItem, List[AssetizableItem]]):
        if not isinstance(item, list):
            items_to_add = [item]
        else:
            items_to_add = item
        for i in items_to_add:
            if isinstance(i, Experiment):
                self.related_experiments.append(item)
            elif isinstance(i, Simulation):
                self.related_simulations.append(item)
            elif isinstance(i, IWorkflowItem):
                self.related_work_items.append(item)
            else:
                raise ValueError("We can only assetize the output of experiments, simulations, and workitems")

            # we call after we know the item has an id
            hook = partial(AssetizeOutput.__create_after_other_items_have_been_created, self)
            i.add_post_creation_hook(hook)
