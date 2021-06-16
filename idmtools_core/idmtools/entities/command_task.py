"""
Command Task is the simplest task. It defined a simple task object with a command line.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import List, Callable, Type, Union, TYPE_CHECKING
from idmtools.assets import AssetCollection
from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification
from idmtools.entities.simulation import Simulation

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass()
class CommandTask(ITask):
    """
    CommandTask is the simplest task.

    A CommandTask is basically a command line and assets.
    """
    #: Hooks to gather common assets
    gather_common_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)
    #: Hooks to gather transient assets
    gather_transient_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)
    """
    Defines an extensible simple task that implements functionality through optional supplied use hooks
    """

    def __post_init__(self):
        """
        Post init.

        Returns:
            None
        """
        super().__post_init__()
        if self.command is None:
            raise ValueError("Command is required")

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather common(experiment-level) assets for task.

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
        Gather transient(experiment-level) assets for task.

        Returns:
            AssetCollection containing transient assets
        """
        ac = AssetCollection()
        for x in self.gather_transient_asset_hooks:
            ac += x(self)
        ac += self.transient_assets
        if len(ac.assets) != 0:
            self.transient_assets = ac
        return ac

    def reload_from_simulation(self, simulation: 'Simulation'):  # noqa: F821
        """
        Reload task from a simulation.

        Args:
            simulation: Simulation to load

        Returns:
            None
        """
        pass

    def pre_creation(self, parent: Union['Simulation', 'IWorkflowItem'], platform: 'IPlatform'):
        """
        pre-creation for the command task.

        The default is to set the windows on the command line based on the platform.

        Args:
            parent: Parent of task
            platform: Platform we are going to pre-creation

        Returns:
            None
        """
        super().pre_creation(parent, platform)
        if platform.is_windows_platform(parent):
            self.command.is_windows = True


class CommandTaskSpecification(TaskSpecification):
    """
    CommandTaskSpecification is the plugin definition for CommandTask.
    """

    def get(self, configuration: dict) -> CommandTask:
        """
        Get instance of CommandTask with configuration.

        Args:
            configuration: configuration for CommandTask

        Returns:
            CommandTask with configuration
        """
        return CommandTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin.

        Returns:
            Plugin description
        """
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"

    def get_example_urls(self) -> List[str]:
        """
        Get example urls related to CommandTask.

        Returns:
            List of urls that have examples related to CommandTask
        """
        return ['https://github.com/InstituteforDiseaseModeling/corvid-idmtools']

    def get_type(self) -> Type[CommandTask]:
        """
        Get task type provided by plugin.

        Returns:
            CommandTask
        """
        return CommandTask

    def get_version(self) -> str:
        """
        Get version of command task plugin.

        Returns:
            Version of plugin
        """
        from idmtools import __version__
        return __version__
