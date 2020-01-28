import os
from dataclasses import dataclass, field
from typing import Optional, List

from idmtools.assets.asset import Asset
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.entities.iexperiment import IDockerExperiment
from idmtools_models.r.r_simulation import RSimulation


@dataclass(repr=False)
class RExperiment(Experiment, IDockerExperiment):
    image_name: str = field(default=None, metadata={"md": True})
    model_path: str = field(default=None, compare=False, metadata={"md": True})
    extra_libraries: list = field(default_factory=lambda: [], compare=False, metadata={"md": True})
    r_path: str = field(default='Rscript')
    config_param: Optional[str] = field(default=None)
    extra_script_args: Optional[List[str]] = field(default=None)
    config_file_name: str = field(default='config.json')
    add_config_file: bool = field(default=True)

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=RSimulation)
        if self.model_path:
            self.model_path = os.path.abspath(self.model_path)

    def gather_assets(self):
        self.assets.add_asset(Asset(absolute_path=self.model_path), fail_on_duplicate=False)

    def pre_creation(self):
        # we don't want to check this until here since analysis could have issues
        if self.image_name is None:
            raise ValueError("image_name is required for R experiments")

        super().pre_creation()
        self.build_image()

        # Create the command line according to the location of the model
        commands_args = [self.r_path, f"./Assets/{os.path.basename(self.model_path)}"]
        if self.extra_script_args:
            commands_args.append(self.extra_script_args)
        if self.config_param:
            commands_args.append(self.config_param)
        if self.add_config_file:
            commands_args.append(self.config_file_name)
        self.command = CommandLine(*commands_args)
