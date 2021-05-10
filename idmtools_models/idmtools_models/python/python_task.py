"""idmtools python task.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import Set, List, Type, Union, TYPE_CHECKING
from idmtools.assets import Asset, AssetCollection
from idmtools.entities import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)


@dataclass()
class PythonTask(ITask):
    """
    PythonTask makes running python scripts a bit easier through idmtools.

    Notes:
        TODO - Link examples here
    """
    script_path: str = field(default=None, metadata={"md": True})
    python_path: str = field(default='python', metadata={"md": True})
    platform_requirements: Set[PlatformRequirements] = field(default_factory=lambda: [PlatformRequirements.PYTHON])

    def __post_init__(self):
        """
        Constructor.
        """
        super().__post_init__()
        if os.path.exists(self.script_path):
            if self.script_path:
                self.script_path = os.path.abspath(self.script_path)
        else:
            # don't error if we can't find script. Maybe it is in the asset collection? but warn user
            logger.warning(f'Cannot find script at {self.script_path}. If script does not exist in Assets '
                           f'as {os.path.basename(self.script_path)}, execution could fail')
        if self.command is None:
            self.command = CommandLine('')

    def gather_common_assets(self) -> AssetCollection:
        """
        Get the common assets. This should be a set of assets that are common to all tasks in an experiment.

        Returns:
            AssetCollection
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug('Adding Common asset from %s', self.script_path)
        self.common_assets.add_or_replace_asset(Asset(absolute_path=self.script_path))
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient assets. Generally this is the simulation level assets.

        Returns:
            Transient assets. Also known as simulation level assets.
        """
        return self.transient_assets

    def reload_from_simulation(self, simulation: Simulation, **kwargs):
        """
        Reloads a python task from a simulation.

        Args:
            simulation: Simulation to reload

        Returns:
            None
        """
        # check experiment level assets for items
        if simulation.parent.assets:
            new_assets = AssetCollection()
            for _i, asset in enumerate(simulation.parent.assets.assets):
                if asset.filename != self.script_path and asset.absolute_path != self.script_path:
                    new_assets.add_asset(asset)
            simulation.parent.assets = new_assets

        logger.debug("Reload from simulation")

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Called before creation of parent.

        Args:
            parent: Parent
            platform: Platform Python Task is being executed on

        Returns:
            None

        Raise:
            ValueError if script name is not provided
        """
        if self.script_path is None:
            raise ValueError("Script name is required")
        self.command = CommandLine.from_string(f'{self.python_path} {platform.join_path(platform.common_asset_path, os.path.basename(self.script_path))}')


class PythonTaskSpecification(TaskSpecification):
    """
    PythonTaskSpecification provides the plugin info for PythonTask.
    """

    def get(self, configuration: dict) -> PythonTask:
        """
        Get instance of Python Task with specified configuration.

        Args:
            configuration: Configuration for task

        Returns:
            Python task
        """
        return PythonTask(**configuration)

    def get_description(self) -> str:
        """
        Description of the plugin.

        Returns:
            Description string
        """
        return "Defines a python script command"

    def get_example_urls(self) -> List[str]:
        """
        Return List of urls that have examples using PythonTask.

        Returns:
            List of urls(str) that point to examples
        """
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['load_lib']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_type(self) -> Type[PythonTask]:
        """
        Get Type for Plugin.

        Returns:
            PythonTask
        """
        return PythonTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
