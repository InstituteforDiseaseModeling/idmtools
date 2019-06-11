import os
import subprocess
import tempfile

from idmtools.assets.Asset import Asset
from idmtools.entities import IExperiment, CommandLine
from idmtools_models.python.PythonSimulation import PythonSimulation


class PythonExperiment(IExperiment):
    def __init__(self, name, model_path, assets=None, extra_libraries=None):
        super().__init__(name=name, assets=assets, simulation_type=PythonSimulation)
        self.model_path = os.path.abspath(model_path)
        self.extra_libraries = extra_libraries or []

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
        self.command = CommandLine("python", f"./Assets/{os.path.basename(self.model_path)}", "config.json")



