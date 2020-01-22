from dataclasses import field, dataclass
from idmtools.assets import Asset, AssetCollection
from idmtools.entities import CommandLine
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.docker_task import DockerTask
import os


@dataclass
class RTask(DockerTask):
    script_name: str = field(default=None)
    r_path: str = field(default='Rscript')
    extra_libraries: list = field(default_factory=lambda: [], compare=False, metadata={"md": True})

    def __post_init__(self):
        super().__post_init__()
        if self.script_name is None:
            raise ValueError("Script name is required")
        cmd_str = f'{self.r_path} ./Assets/{os.path.basename(self.script_name)}'
        self._task_log.info('Setting command line to %0', cmd_str)
        self.command = CommandLine(cmd_str)

    def reload_from_simulation(self, simulation: Simulation):
        pass

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather R Assets
        Returns:

        """
        super().gather_common_assets()
        self._task_log.info('Adding Common asset from %0', self.script_name)
        self.common_assets.add_asset(Asset(absolute_path=self.script_name), fail_on_duplicate=False)
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient assets. Generally this is the simulation level assets

        Returns:

        """
        return self.transient_assets


class RTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> RTask:
        return RTask(**configuration)

    def get_description(self) -> str:
        return "Defines a R script command"

