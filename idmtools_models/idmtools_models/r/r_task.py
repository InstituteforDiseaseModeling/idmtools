"""idmtools rtask.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from dataclasses import field, dataclass
from logging import getLogger, DEBUG
from typing import Type, Union, TYPE_CHECKING
from idmtools.assets import Asset, AssetCollection
from idmtools.core.docker_task import DockerTask
from idmtools.entities import CommandLine
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform


@dataclass
class RTask(DockerTask):
    """
    Defines an RTask for idmtools. Currently only useful for local platform.

    Notes:
        - TODO rework this to be non-docker
    """
    script_path: str = field(default=None, metadata={"md": True})
    r_path: str = field(default='Rscript', metadata={"md": True})

    def __post_init__(self):
        """Constructor."""
        super().__post_init__()
        cmd_str = f'{self.r_path} ./Assets/{os.path.basename(self.script_path)}'
        if logger.isEnabledFor(DEBUG):
            logger.info('Setting command line to %s', cmd_str)
        self.command = CommandLine.from_string(cmd_str)

    def reload_from_simulation(self, simulation: Simulation, **kwargs):
        """
        Reload RTask from a simulation. Used when fetching an simulation to do a recreation.

        Args:
            simulation: Simulation object containing our metadata to rebuild task
            **kwargs:

        Returns:
            None
        """
        logger.debug("Reload from simulation")
        # check experiment level assets for items
        if simulation.parent.assets:
            new_assets = AssetCollection()
            for _i, asset in enumerate(simulation.parent.assets.assets):
                if asset.filename != self.script_path and asset.absolute_path != self.script_path:
                    new_assets.add_asset(asset)
            simulation.parent.assets = new_assets

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather R Assets.

        Returns:
            Common assets
        """
        super().gather_common_assets()
        if logger.isEnabledFor(DEBUG):
            logger.info('Adding Common asset from %s', self.script_path)
        self.common_assets.add_or_replace_asset(Asset(absolute_path=self.script_path))
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient assets. Generally this is the simulation level assets.

        Returns:
            Transient assets(Simulation level Assets)
        """
        return self.transient_assets

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Called before creation of parent.

        Args:
            parent: Parent
            platform: Platform R Task is executing on

        Returns:
            None

        Raise:
            ValueError if script name is not provided
        """
        if self.script_path is None:
            raise ValueError("Script name is required")

        self.command = CommandLine.from_string(f'{self.r_path} {platform.join_path(platform.common_asset_path, os.path.basename(self.script_path))}')


class RTaskSpecification(TaskSpecification):
    """
    RTaskSpecification defines plugin specification for RTask.
    """

    def get(self, configuration: dict) -> RTask:
        """
        Get instance of RTask.

        Args:
            configuration: configuration for task

        Returns:
            RTask with configuration
        """
        return RTask(**configuration)

    def get_description(self) -> str:
        """
        Returns the Description of the plugin.

        Returns:
            Plugin Description
        """
        return "Defines a R script command"

    def get_type(self) -> Type[RTask]:
        """
        Get Type for Plugin.

        Returns:
            RTask
        """
        return RTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
