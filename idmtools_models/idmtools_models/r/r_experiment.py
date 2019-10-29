import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Optional, List

from idmtools.assets.asset import Asset
from idmtools.entities import CommandLine, IExperiment
from idmtools.entities.iexperiment import IDockerExperiment
from idmtools_models.python.python_simulation import PythonSimulation


@dataclass(repr=False)
class RExperiment(IExperiment, IDockerExperiment):
    image_name: str = field(default=None, metadata={"md": True})
    model_path: str = field(default=None, compare=False, metadata={"md": True})
    extra_libraries: list = field(default_factory=lambda: [], compare=False, metadata={"md": True})
    r_path: str = field(default='Rscript')
    config_param: Optional[str] = field(default=None)
    extra_script_args: Optional[List[str]] = field(default=None)
    config_file_name: str = field(default='config.json')
    add_config_file: bool = field(default=True)

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=PythonSimulation)
        if self.image_name is None:
            raise ValueError("image_name is required for R experiments")
        if self.model_path:
            self.model_path = os.path.abspath(self.model_path)

    def retrieve_python_dependencies(self):
        """
        Retrieve the Pypi libraries associated with the given model script.
        Notes:
            This function scan recursively through the whole  directory where the model file is contained.
            This function relies on pipreqs being installed on the system to provide dependencies list.

        Returns:
            List of libraries required by the script
        """
        model_folder = os.path.dirname(self.model_path)

        # Store the pipreqs file in a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            reqs_file = os.path.join(tmpdir, "reqs.txt")
            subprocess.run(['pipreqs', '--savepath', reqs_file, model_folder], stderr=subprocess.DEVNULL)

            # Reads through the reqs file to get the libraries
            with open(reqs_file, 'r') as fp:
                extra_libraries = [line.strip() for line in fp.readlines()]

        return extra_libraries

    def gather_assets(self):
        self.assets.add_asset(Asset(absolute_path=self.model_path), fail_on_duplicate=False)

    def pre_creation(self):
        super().pre_creation()

        # Create the command line according to the location of the model
        commands_args = [self.r_path, f"./Assets/{os.path.basename(self.model_path)}"]
        if self.extra_script_args:
            commands_args.append(self.extra_script_args)
        if self.config_param:
            commands_args.append(self.config_param)
        if self.add_config_file:
            commands_args.append(self.config_file_name)
        self.command = CommandLine(*commands_args)


