from dataclasses import dataclass
from typing import Optional, Type
from idmtools.assets import AssetCollection
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
