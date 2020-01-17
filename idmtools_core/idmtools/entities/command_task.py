from dataclasses import dataclass, field
from typing import List, Callable, NoReturn
from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification


@dataclass
class CommandTask(ITask):
    """
    Defines an extensible simple task that implements functionality through optional supplied use hooks
    """
    gather_asset_hooks: List[Callable[[], NoReturn]] = field(default_factory=list)

    def gather_assets(self) -> NoReturn:
        [x() for x in self.gather_asset_hooks]


class CommandTaskSpecification(TaskSpecification):
    def get(self, configuration: dict) -> 'ITask':
        return CommandTask(**configuration)

    def get_description(self) -> str:
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"
