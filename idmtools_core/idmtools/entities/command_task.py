from dataclasses import dataclass, field
from typing import List, Callable

from idmtools.assets import AssetCollection
from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification


@dataclass()
class CommandTask(ITask):
    gather_common_asset_hooks: List[Callable[[], AssetCollection]] = field(default_factory=list)
    gather_transient_asset_hooks: List[Callable[[], AssetCollection]] = field(default_factory=list)
    """
    Defines an extensible simple task that implements functionality through optional supplied use hooks
    """

    def __post_init__(self):
        super().__post_init__()
        if self.command is None:
            raise ValueError("Command is required")

    def gather_common_assets(self) -> AssetCollection:
        # TODO validate hooks have expected return type
        ac = AssetCollection()
        for x in self.gather_common_asset_hooks:
            ac += x(self)
        return ac

    def gather_transient_assets(self) -> AssetCollection:
        ac = AssetCollection()
        for x in self.gather_transient_asset_hooks:
            ac += x(self)
        #self.transient_assets = ac   # this will make other case fail
        return ac

    def reload_from_simulation(self, simulation: 'Simulation'):
        pass


class CommandTaskSpecification(TaskSpecification):
    def get(self, configuration: dict) -> 'ITask':
        return CommandTask(**configuration)

    def get_description(self) -> str:
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"
