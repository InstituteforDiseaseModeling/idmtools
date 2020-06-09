from dataclasses import dataclass, field
from typing import List, Callable, Type

from idmtools.assets import AssetCollection
from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification


@dataclass()
class CommandTask(ITask):
    #: Hooks to gather common assets
    gather_common_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)
    #: Hooks to gather transient assets
    gather_transient_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)
    """
    Defines an extensible simple task that implements functionality through optional supplied use hooks
    """

    def __post_init__(self):
        super().__post_init__()
        if self.command is None:
            raise ValueError("Command is required")

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather common(experiment-level) assets for task

        Returns:
            AssetCollection containing common assets
        """
        # TODO validate hooks have expected return type
        ac = AssetCollection()
        for x in self.gather_common_asset_hooks:
            ac += x(self)
        ac += self.common_assets
        return ac

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient(experiment-level) assets for task

        Returns:
            AssetCollection containing transient assets
        """
        ac = AssetCollection()
        for x in self.gather_transient_asset_hooks:
            ac += x(self)
        if len(ac.assets) != 0:
            self.transient_assets = ac
        ac += self.transient_assets
        return ac

    def reload_from_simulation(self, simulation: 'Simulation'):  # noqa: F821
        pass


class CommandTaskSpecification(TaskSpecification):
    def get(self, configuration: dict) -> CommandTask:
        """
        Get instance of CommandTask with configuration

        Args:
            configuration: configuration for CommandTask

        Returns:
            CommandTask with configuration
        """
        return CommandTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin

        Returns:
            Plugin description
        """
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"

    def get_example_urls(self) -> List[str]:
        """
        Get example urls related to CommandTask

        Returns:
            List of urls that have examples related to CommandTask
        """
        return ['https://github.com/InstituteforDiseaseModeling/corvid-idmtools']

    def get_type(self) -> Type[CommandTask]:
        """
        Get task type provided by plugin

        Returns:
            CommandTask
        """
        return CommandTask
