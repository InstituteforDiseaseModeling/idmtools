"""idmtools jsonr task.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Optional, List, Type, Union, TYPE_CHECKING
from idmtools.assets import AssetCollection
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_models.r.r_task import RTask
if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform


@dataclass
class JSONConfiguredRTask(JSONConfiguredTask, RTask):
    """
    JSONConfiguredRTask combines JSONConfiguredTask and RTask.

    Notes:
        - TODO Add example references here

    See Also:
        :class:`idmtools_models.json_configured_task.JSONConfiguredTask`
        :class:`idmtools_models.r.r_task.RTask`
    """
    configfile_argument: Optional[str] = field(default="--config", metadata={"md": True})

    def __post_init__(self):
        """Constructor."""
        JSONConfiguredTask.__post_init__(self)
        RTask.__post_init__(self)

    def gather_common_assets(self):
        """
        Return the common assets for a JSON Configured Task.

        Returns:
            Assets
        """
        return RTask.gather_common_assets(self)

    def gather_transient_assets(self) -> AssetCollection:
        """
        Get Transient assets. This should general be the config.json.

        Returns:
            Transient assets
        """
        return JSONConfiguredTask.gather_transient_assets(self)

    def reload_from_simulation(self, simulation: Simulation, **kwargs):
        """
        Reload task details from a simulation. Used in some fetch operations.

        Args:
            simulation: Simulation that is parent item
            **kwargs:

        Returns:
            None
        """
        JSONConfiguredTask.reload_from_simulation(self, simulation, **kwargs)
        RTask.reload_from_simulation(self, simulation, **kwargs)

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Pre-creation event.

        Proxy calls to JSONConfiguredTask and RTask

        Args:
            parent: Parent item
            platform: Platform item is being created on

        Returns:
            None
        """
        RTask.pre_creation(self, parent, platform)
        JSONConfiguredTask.pre_creation(self, parent, platform)

    def post_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Post-creation of task.

        Proxy calls to JSONConfiguredTask and RTask

        Args:
            parent: Parent item
            platform: Platform we are executing on

        Returns:
            None
        """
        JSONConfiguredTask.post_creation(self, parent, platform)
        RTask.post_creation(self, parent, platform)


class JSONConfiguredRTaskSpecification(TaskSpecification):
    """
    JSONConfiguredRTaskSpecification provides the plugin info for JSONConfiguredRTask.
    """

    def get(self, configuration: dict) -> JSONConfiguredRTask:
        """
        Get instance of JSONConfiguredRTaskSpecification with configuration provided.

        Args:
            configuration: Configuration for object

        Returns:
            JSONConfiguredRTaskSpecification with configuration
        """
        return JSONConfiguredRTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin.

        Returns:
            Description of plugin
        """
        return "Defines a R script that has a single JSON config file"

    def get_example_urls(self) -> List[str]:
        """
        Get Examples for JSONConfiguredRTask.

        Returns:
            List of Urls that point to examples for JSONConfiguredRTask
        """
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['r_model']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_type(self) -> Type[JSONConfiguredRTask]:
        """
        Get Type for Plugin.

        Returns:
            JSONConfiguredRTask
        """
        return JSONConfiguredRTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
