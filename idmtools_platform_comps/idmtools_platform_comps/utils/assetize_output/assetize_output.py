from dataclasses import dataclass, field
from typing import List, Union
from idmtools.entities.experiment import Experiment
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
            command += f"--simulation {wi.id} "

    def pre_creation(self) -> None:
        super().pre_creation()

    def run_after(self, item: Union[Experiment, Simulation, IWorkflowItem]):
        if isinstance(item, Experiment):
            self.related_experiments.append(item)
        elif isinstance(item, Simulation):
            self.related_simulations.append(item)
        elif isinstance(item, IWorkflowItem):
            self.related_work_items.append(item)
        else:
            raise ValueError("We can only assestize the output of experiments, simulations, and workitems")

        # we call after we know the item has an id
        #item.post_creation_hooks.append()