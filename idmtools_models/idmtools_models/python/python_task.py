import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from logging import getLogger
from typing import Set, List

from idmtools.assets import Asset, AssetCollection
from idmtools.entities import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)


@dataclass()
class PythonTask(ITask):
    script_path: str = None
    python_path: str = 'python'
    platform_requirements: Set[PlatformRequirements] = field(default_factory=lambda: [PlatformRequirements.PYTHON])

    def __post_init__(self):
        super().__post_init__()
        if self.script_path is None:
            raise ValueError("Script name is required")
        if os.path.exists(self.script_path):
            self.script_path = os.path.abspath(self.script_path)
        else:
            # don't error if we can't find script. Maybe it is in the asset collection? but warn user
            logger.warning(f'Cannot find script at {self.script_path}. If script does not exist in Assets '
                           f'as {os.path.basename(self.script_path)}, execution could fail')
        self.command = CommandLine()

    @property
    def command(self):
        """
        Update executable with new python_path
        Returns: re-build command
        """
        cmd_str = f'{self.python_path} ./Assets/{os.path.basename(self.script_path)}'
        if self._command:
            self._command._executable = cmd_str
            self._task_log.info('Setting command line to %s', cmd_str)

        return self._command

    @command.setter
    def command(self, command):
        self._command = command

    def retrieve_python_dependencies(self):
        """
        Retrieve the Pypi libraries associated with the given model script.
        Notes:
            This function scan recursively through the whole  directory where the model file is contained.
            This function relies on pipreqs being installed on the system to provide dependencies list.

        Returns:
            List of libraries required by the script
        """
        model_folder = os.path.dirname(self.script_path)

        # Store the pipreqs file in a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            reqs_file = os.path.join(tmpdir, "reqs.txt")
            subprocess.run(['pipreqs', '--savepath', reqs_file, model_folder], stderr=subprocess.DEVNULL)

            # Reads through the reqs file to get the libraries
            with open(reqs_file, 'r') as fp:
                extra_libraries = [line.strip() for line in fp.readlines()]

        return extra_libraries

    def gather_common_assets(self) -> AssetCollection:
        """
        Get the common assets. This should be a set of assets that are common to all tasks in an experiment

        Returns:
            AssetCollection
        """
        # ensure that assets is in collection
        self._task_log.info('Adding Common asset from %s', self.script_path)
        self.common_assets.add_or_replace_asset(Asset(absolute_path=self.script_path))
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient assets. Generally this is the simulation level assets

        Returns:

        """
        return self.transient_assets

    def reload_from_simulation(self, simulation: Simulation):
        """
        Reloads a python task from a simulation

        Args:
            simulation: Simulation to reload

        Returns:

        """
        # We have no configs so nothing to reload
        pass


class PythonTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> PythonTask:
        return PythonTask(**configuration)

    def get_description(self) -> str:
        return "Defines a python script command"

    def get_example_urls(self) -> List[str]:
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['load_lib']]
        return [self.get_version_url(__version__, x) for x in examples]
