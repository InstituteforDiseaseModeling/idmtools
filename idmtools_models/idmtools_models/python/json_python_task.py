from dataclasses import dataclass
from typing import Optional, Type, Union
from idmtools.assets import AssetCollection
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_models.python.python_task import PythonTask


@dataclass
class JSONConfiguredPythonTask(JSONConfiguredTask, PythonTask):
    configfile_argument: Optional[str] = "--config"

    def __post_init__(self):
        super().__post_init__()
        if self.configfile_argument is not None:
            self.command.add_option(self.configfile_argument, self.config_file_name)

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

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        """
        Pre-creation

        Args:
            parent:

        Returns:
            None
        See Also
            :meth:`idmtools_models.json_configured_task.JSONConfiguredTask.pre_creation`
            :meth:`idmtools_models.python.python_task.PythonTask.pre_creation`
        """
        JSONConfiguredTask.pre_creation(self, parent)
        PythonTask.pre_creation(self, parent)

    def post_creation(self, parent: Union[Simulation, IWorkflowItem]):
        """
        Post-creation

        Args:
            parent: Parent

        Returns:

        See Also
            :meth:`idmtools_models.json_configured_task.JSONConfiguredTask.post_creation`
            :meth:`idmtools_models.python.python_task.PythonTask.post_creation`
        """
        JSONConfiguredTask.post_creation(self, parent)
        PythonTask.post_creation(self, parent)


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
