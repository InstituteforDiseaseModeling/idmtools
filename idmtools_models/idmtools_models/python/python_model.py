import json
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import List, NoReturn
from idmtools.assets.asset import Asset
from idmtools.entities import CommandLine
from idmtools.entities.imodel import IModel
from idmtools.entities.itask import PlatformRequirement


@dataclass(repr=False)
class PythonModel(IModel):
    model_path: str = field(default=None, compare=False, metadata={"md": True})
    extra_libraries: list = field(default_factory=lambda: [], compare=False, metadata={"md": True})
    platform_requirements: List[PlatformRequirement] = field(
        default_factory=lambda: [PlatformRequirement.PYTHON_SCRIPTING],
        compare=False, metadata={"md": True})
    python_path: str = 'python'
    config = dict()

    def __post_init__(self):
        super().__post_init__()
        if self.model_path:
            self.model_path = os.path.abspath(self.model_path)

        self.command = CommandLine(self.python_path, f"./Assets/{os.path.basename(self.model_path)}", "config.json")

    def pre_experiment_creation(self):
        pass

    def pre_simulation_creation(self):
        pass

    def gather_experiment_assets(self):
        return [Asset(absolute_path=self.model_path)]

    def gather_assets(self) -> NoReturn:
        self.add_assets([Asset(filename="config.json", content=json.dumps(self.config))])

    def set_parameter(self, name, value):
        self.config[name] = value

    def get_parameter(self, name, value):
        return self.config[name]

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


class IDockerTask(object):
    pass


# @dataclass(repr=False)
# class DockerPython(PythonModel, IDockerTask):
#     image_name: str
#     command:
#
#     def __post_init__(self):
#         self.command = CommandLine("docker", "run", "-v", "{data_path}:/workdir", f"{self.image_name}", "python",
#                                    f"./Assets/{os.path.basename(self.model_path)}", "config.json")

