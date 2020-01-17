import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import NoReturn, Optional, Set
from idmtools.assets import Asset
from idmtools.entities import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.registry.task_specification import TaskSpecification
from idmtools_models.json_configured_task import JSONConfiguredTask


@dataclass()
class PythonTask(ITask):
    def reload_from_simulation(self, simulation: 'Simulation'):
        pass

    script_name: str = None
    python_path: str = 'python'
    platform_requirements: Set[PlatformRequirements] = field(default_factory=lambda: [PlatformRequirements.PYTHON])

    def __post_init__(self):
        super().__post_init__()
        if self.script_name is None:
            raise ValueError("Script name is required")
        self.command = CommandLine(f'{self.python_path} ./Assets/{os.path.basename(self.script_name)}')

    def retrieve_python_dependencies(self):
        """
        Retrieve the Pypi libraries associated with the given model script.
        Notes:
            This function scan recursively through the whole  directory where the model file is contained.
            This function relies on pipreqs being installed on the system to provide dependencies list.

        Returns:
            List of libraries required by the script
        """
        model_folder = os.path.dirname(self.script_name)

        # Store the pipreqs file in a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            reqs_file = os.path.join(tmpdir, "reqs.txt")
            subprocess.run(['pipreqs', '--savepath', reqs_file, model_folder], stderr=subprocess.DEVNULL)

            # Reads through the reqs file to get the libraries
            with open(reqs_file, 'r') as fp:
                extra_libraries = [line.strip() for line in fp.readlines()]

        return extra_libraries

    def gather_assets(self) -> NoReturn:
        self.assets.add_asset(Asset(absolute_path=self.script_name), fail_on_duplicate=False)


@dataclass
class JSONConfiguredPythonTask(JSONConfiguredTask, PythonTask):
    configfile_argument: Optional[str] = "--config"

    def __post_init__(self):
        super().__post_init__()
        if self.configfile_argument is not None:
            self.command.add_option(self.configfile_argument, self.config_file_name)

    def gather_assets(self):
        PythonTask.gather_assets(self)
        JSONConfiguredTask.gather_assets(self)


class PythonTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> PythonTask:
        return PythonTask(**configuration)

    def get_description(self) -> str:
        return "Defines a python script command"


class JSONConfiguredPythonTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredPythonTask:
        return JSONConfiguredPythonTask(**configuration)

    def get_description(self) -> str:
        return "Defines a python script that has a single JSON config file"
