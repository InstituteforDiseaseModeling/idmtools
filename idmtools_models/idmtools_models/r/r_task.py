from dataclasses import field, dataclass
from typing import NoReturn, Optional, Set
from idmtools.assets import Asset
from idmtools.entities import CommandLine
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.docker_task import DockerTask
from idmtools_models.json_configured_task import JSONConfiguredTask
import os

@dataclass
class RTask(DockerTask):
    script_name: str = field(default=None)
    r_path: str = field(default='Rscript')
    extra_libraries: list = field(default_factory=lambda: [], compare=False, metadata={"md": True})
    platform_requirements: Set[PlatformRequirements] = field(default_factory=lambda: [PlatformRequirements.DOCKER])

    def __post_init__(self):
        if self.script_name is None:
            raise ValueError("Script name is required")
        self.command = CommandLine(f'{self.r_path} ./Assets/{os.path.basename(self.script_name)}')

    def reload_from_simulation(self, simulation: Simulation):
        pass

    def gather_assets(self) -> NoReturn:
        super().gather_assets()
        self.assets.add_asset(Asset(absolute_path=self.script_name), fail_on_duplicate=False)


@dataclass
class JSONConfiguredRTask(JSONConfiguredTask, RTask):
    configfile_argument: Optional[str] = "--config"

    def __post_init__(self):
        super().__post_init__()
        if self.configfile_argument is not None:
            self.command.add_option(self.configfile_argument, self.config_file_name)

    def gather_assets(self):
        RTask.gather_assets(self)
        JSONConfiguredTask.gather_assets(self)


class RTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> RTask:
        return RTask(**configuration)

    def get_description(self) -> str:
        return "Defines a R script command"


class JSONConfiguredRTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredRTask:
        return JSONConfiguredRTask(**configuration)

    def get_description(self) -> str:
        return "Defines a R script that has a single JSON config file"
