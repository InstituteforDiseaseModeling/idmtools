from dataclasses import dataclass, field
from typing import Optional, List, Type, Union
from idmtools.assets import AssetCollection
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_models.r.r_task import RTask


@dataclass
class JSONConfiguredRTask(JSONConfiguredTask, RTask):
    configfile_argument: Optional[str] = field(default="--config", metadata={"md": True})

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
        return RTask.gather_common_assets(self)

    def gather_transient_assets(self) -> AssetCollection:
        """
        Get Transient assets. This should general be the config.json

        Returns:
            Transient assets
        """
        return JSONConfiguredTask.gather_transient_assets(self)

    def reload_from_simulation(self, simulation: Simulation, **kwargs):
        JSONConfiguredTask.reload_from_simulation(self, simulation, **kwargs)
        RTask.reload_from_simulation(self, simulation, **kwargs)

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        JSONConfiguredTask.pre_creation(self, parent)
        RTask.pre_creation(self, parent)

    def post_creation(self, parent: Union[Simulation, IWorkflowItem]):
        JSONConfiguredTask.post_creation(self, parent)
        RTask.post_creation(self, parent)


class JSONConfiguredRTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredRTask:
        """
        Get instance of JSONConfiguredRTaskSpecification with configuration provided

        Args:
            configuration: Configuration for object

        Returns:
            JSONConfiguredRTaskSpecification with configuration
        """
        return JSONConfiguredRTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin

        Returns:
            Description of plugin
        """
        return "Defines a R script that has a single JSON config file"

    def get_example_urls(self) -> List[str]:
        """
        Get Examples for JSONConfiguredRTask

        Returns:
            List of Urls that point to examples for JSONConfiguredRTask
        """
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['r_model']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_type(self) -> Type[JSONConfiguredRTask]:
        """
        Get Type for Plugin

        Returns:
            JSONConfiguredRTask
        """
        return JSONConfiguredRTask
