from dataclasses import dataclass, field
from typing import Optional, Type, Union, TYPE_CHECKING, Set
from idmtools.assets import AssetCollection
from idmtools.entities.itask import ITask
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_models.python.python_task import PythonTask

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform


@dataclass
class JSONConfiguredPythonTask(JSONConfiguredTask, PythonTask):
    configfile_argument: Optional[str] = field(default="--config")

    def __post_init__(self):
        JSONConfiguredTask.__post_init__(self)
        PythonTask.__post_init__(self)

    def gather_common_assets(self):
        """
        Return the common assets for a JSON Configured Task
        a derived class
        Returns:

        """
        return PythonTask.gather_common_assets(self)

    def gather_transient_assets(self) -> AssetCollection:
        """
        Get Transient assets. This should general be the config.json

        Returns:
            Transient assets
        """
        return JSONConfiguredTask.gather_transient_assets(self)

    def reload_from_simulation(self, simulation: Simulation, **kwargs):
        """
        Reload the task from a simulation

        Args:
            simulation: Simulation to reload from
            **kwargs:

        Returns:
            None

        See Also
            :meth:`idmtools_models.json_configured_task.JSONConfiguredTask.reload_from_simulation`
            :meth:`idmtools_models.python.python_task.PythonTask.reload_from_simulation`
        """
        JSONConfiguredTask.reload_from_simulation(self, simulation, **kwargs)
        PythonTask.reload_from_simulation(self, simulation, **kwargs)

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Pre-creation

        Args:
            parent: Parent of task
            platform: Platform Python Script is being executed on

        Returns:
            None
        See Also
            :meth:`idmtools_models.json_configured_task.JSONConfiguredTask.pre_creation`
            :meth:`idmtools_models.python.python_task.PythonTask.pre_creation`
        """
        JSONConfiguredTask.pre_creation(self, parent, platform)
        PythonTask.pre_creation(self, parent, platform)

    def post_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Post-creation

        Args:
            parent: Parent
            platform: Platform Python Script is being executed on

        Returns:

        See Also
            :meth:`idmtools_models.json_configured_task.JSONConfiguredTask.post_creation`
            :meth:`idmtools_models.python.python_task.PythonTask.post_creation`
        """
        JSONConfiguredTask.post_creation(self, parent, platform)
        PythonTask.post_creation(self, parent, platform)


class JSONConfiguredPythonTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredPythonTask:
        """
        Get  instance of JSONConfiguredPythonTask with configuration

        Args:
            configuration: Configuration for task

        Returns:
            JSONConfiguredPythonTask with configuration
        """
        return JSONConfiguredPythonTask(**configuration)

    def get_description(self) -> str:
        """
        Get description for plugin

        Returns:
            Plugin Description
        """
        return "Defines a python script that has a single JSON config file"

    def get_type(self) -> Type[JSONConfiguredPythonTask]:
        """
        Get Type for Plugin

        Returns:
            JSONConfiguredPythonTask
        """
        return JSONConfiguredPythonTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
