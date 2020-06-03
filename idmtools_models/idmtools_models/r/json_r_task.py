from dataclasses import dataclass
from typing import Optional, List
from idmtools.assets import AssetCollection
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.json_configured_task import JSONConfiguredTask
from idmtools_models.r.r_task import RTask


@dataclass
class JSONConfiguredRTask(JSONConfiguredTask, RTask):
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
        return RTask.gather_common_assets(self)

    def gather_transient_assets(self) -> AssetCollection:
        """
        Get Transient assets. This should general be the config.json

        Returns:
            Transient assets
        """
        return JSONConfiguredTask.gather_transient_assets(self)


class JSONConfiguredRTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredRTask:
        return JSONConfiguredRTask(**configuration)

    def get_description(self) -> str:
        return "Defines a R script that has a single JSON config file"

    def get_example_urls(self) -> List[str]:
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['r_model']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]
