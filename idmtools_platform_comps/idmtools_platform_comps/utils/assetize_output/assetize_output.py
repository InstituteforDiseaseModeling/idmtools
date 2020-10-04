from dataclasses import dataclass, field
from functools import partial
from typing import List, Union
from idmtools.core import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


@dataclass(repr=False)
class AssetizeOutput(SSMTWorkItem):
    file_patterns: List[str] = field(default=list)

    def __post_init__(self):
        super().__post_init__()

    def create_command(self):
        command = "python3 assetize_output.py "
        for experiment in self.related_experiments:
            command += f"--experiment {experiment.id} "

        for simulation in self.related_simulations:
            command += f"--simulation {simulation.id} "

        for wi in self.related_work_items:
            command += f"--work-item {wi.id} "

    def pre_creation(self, platform: IPlatform) -> None:
        super().pre_creation(platform)

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
        all_created = True
        for item_type in ['related_experiments', 'related_simulations', 'related_work_items']:
            for item in getattr(self, item_type):
                if item.status not in [EntityStatus.CREATED, EntityStatus.RUNNING, EntityStatus.COMMISSIONING, EntityStatus.SUCCEEDED]:
                    all_created = False
                    break
            if all_created is False:
                break
        if all_created:
            self.run(platform=platform)

    def run_after(self, item: Union[Experiment, Simulation, IWorkflowItem]):
        if isinstance(item, Experiment):
            self.related_experiments.append(item)
        elif isinstance(item, Simulation):
            self.related_simulations.append(item)
        elif isinstance(item, IWorkflowItem):
            self.related_work_items.append(item)
        else:
            raise ValueError("We can only assetize the output of experiments, simulations, and workitems")

        # we call after we know the item has an id
        hook = partial(AssetizeOutput.__create_after_other_items_have_been_created, self)
        item.add_post_creation_hook(hook)