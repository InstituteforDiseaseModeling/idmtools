import os
import pathlib
import shutil
from functools import partial
from typing import Any, Dict

import pytest

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

cwd = os.path.dirname(__file__)


@pytest.mark.serial
@linux_only
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.job_directory = "DEST"
        self.platform = Platform('SLURM_LOCAL', job_directory=self.job_directory)


    def tearDown(self):
        shutil.rmtree(self.job_directory)

    def test_sweeping_and_local_folders_creation(self):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model.py"),
                                        parameters=(dict(c=0)))

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(3))
        builder.add_sweep_definition(partial(param_update, param="b"), range(3))
        ts.add_builder(builder)

        # Now we can create our Experiment using our template builder
        experiment = Experiment.from_template(ts, name=self.case_name)
        # Add our own custom tag to simulation
        experiment.tags["tag1"] = 1
        # And add common assets from local dir
        experiment.assets.add_directory(assets_directory=os.path.join(COMMON_INPUT_PATH, "python", "Assets"))

        # Create suite
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        # suite.run(wait_till_done=False)
        suite.run(wait_until_done=False, wait_on_done=False, max_running_jobs=10)
        # Verify local folders and files
        # First verify all files under experiment
        files = []
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(cwd, self.job_directory, suite.id, experiment.id)):
            files.extend(filenames)
            break
        self.assertSetEqual(set(files), set(["metadata.json", "run_simulation.sh", "sbatch.sh"]))

        # verify all files under simulations
        simulations = experiment.simulations.items
        self.assertEqual(len(simulations), 9)
        count = 0
        for simulation in simulations:
            files = []
            for (dirpath, dirnames, filenames) in os.walk(
                    os.path.join(cwd, self.job_directory, suite.id, experiment.id, simulation.id)):
                if dirnames == ["Assets"]:
                    # verify Assets folder under simulation is symlink and it link to experiment's Assets
                    self.assertTrue(os.path.islink(
                        os.path.join(cwd, self.job_directory, suite.id, experiment.id, simulation.id, "Assets")))
                    target_link = os.readlink(
                        os.path.join(cwd, self.job_directory, suite.id, experiment.id, simulation.id, "Assets"))
                    self.assertEqual(os.path.basename(pathlib.Path(target_link).parent), experiment.id)
                    count = count + 1
                files.extend(filenames)
                break
            self.assertSetEqual(set(files), set(["metadata.json", "_run.sh", "config.json"]))
        self.assertEqual(count, 9)  # make sure we found total 9 symlinks for Assets folder

        # TODO, grab stdout.txt and stderr.txt from remote cluster and validate
        # TODO, test experiment status
        # TODO, test remote files
