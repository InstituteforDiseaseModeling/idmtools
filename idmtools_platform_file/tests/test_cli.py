import os

import shutil
import unittest
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
from idmtools_test.utils.cli import run_command, get_subcommands_from_help_result
from idmtools_test.utils.decorators import linux_only


@pytest.mark.serial
@linux_only
class TestCli(unittest.TestCase):

    def create_experiment(self, platform=None, a=1, b=1, retries=None, wait_until_done=False, wait_on_done=False):
        task = JSONConfiguredPythonTask(script_path=os.path.join(COMMON_INPUT_PATH, "python", "model3.py"),
                                        envelope="parameters", parameters=(dict(c=0)))
        task.python_path = "python3"

        ts = TemplatedSimulations(base_task=task)
        builder = SimulationBuilder()

        def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
            return simulation.task.set_parameter(param, value)

        builder.add_sweep_definition(partial(param_update, param="a"), range(a))
        builder.add_sweep_definition(partial(param_update, param="b"), range(b))
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
        # Commission
        suite.run(platform=platform, wait_until_done=wait_until_done, wait_on_done=wait_on_done, retries=retries)
        print("suite_id: " + suite.id)
        print("experiment_id: " + experiment.id)
        return experiment

    @classmethod
    def setUpClass(cls) -> None:
        cls.job_directory = "DEST-CLI"
        cls.platform = Platform('FILE', job_directory=cls.job_directory)

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            shutil.rmtree(cls.job_directory)
        except:
            print('Error while deleting directory')

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName

        self.experiment = self.create_experiment(self.platform, a=3, b=3)
        self.suite = self.experiment.parent
        self.suite_dir = self.platform.get_directory(self.suite)

    def test_subcommands_exists(self):
        result = run_command('file', '--help')
        print(result.stdout)
        lines = get_subcommands_from_help_result(result)
        self.assertListEqual(lines, ['clear-files', 'get-latest', 'get-path', 'get-status', 'status', 'status-report'])

    def test_clear_files(self):
        result = run_command('file', self.job_directory, 'clear-files', '--exp-id', self.experiment.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

    def test_clear_files_remove_for_sim(self):
        # create file under sim first:
        filename = "random.txt"
        sim_dir = self.platform.get_directory(self.experiment.simulations[0])
        full_path = os.path.join(sim_dir, filename)
        # Create the file using the open() function with 'w' mode
        with open(full_path, 'w') as f:
            pass  # do nothing
        self.assertTrue(os.path.isfile(full_path))
        result = run_command('file', self.job_directory, 'clear-files', '--exp-id', self.experiment.id, '--remove',
                             filename)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        # check if file get removed
        self.assertFalse(os.path.exists(full_path))
        print(result.stdout)

        # test remove folder under sim:
        my_dir = "output"
        full_my_dir = os.path.join(sim_dir, my_dir)
        os.mkdir(full_my_dir)
        self.assertTrue(os.path.isdir(full_my_dir))
        result = run_command('file', self.job_directory, 'clear-files', '--exp-id', self.experiment.id, '--remove',
                             my_dir)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        # verify folder got deleted
        self.assertFalse(os.path.isdir(full_my_dir))

    def test_clear_files_remove_for_exp(self):
        # create file under sim first:
        filename = "random.txt"
        exp_dir = self.platform.get_directory(self.experiment)
        full_path = os.path.join(exp_dir, filename)
        # Create the file using the open() function with 'w' mode
        with open(full_path, 'w') as f:
            pass  # do nothing
        self.assertTrue(os.path.isfile(full_path))
        result = run_command('file', self.job_directory, 'clear-files', '--exp-id', self.experiment.id, '--remove',
                             "somefile.txt")
        self.assertTrue(result.exit_code == 0, msg=result.output)
        # check if file get removed, it should not for experiment
        self.assertTrue(os.path.exists(full_path))
        print(result.stdout)

    def test_get_latest(self):
        result = run_command('file', self.job_directory, 'get-latest')
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

    def test_get_path(self):
        result = run_command('file', self.job_directory, 'get-path', '--exp-id', self.experiment.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        # for suite-id
        result = run_command('file', self.job_directory, 'get-path', '--suite-id', self.suite.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        # for sim-id
        result = run_command('file', self.job_directory, 'get-path', '--sim-id', self.experiment.simulations[0].id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

    def test_get_status(self):
        result = run_command('file', self.job_directory, 'get-status', '--exp-id', self.experiment.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        # for sim-id
        result = run_command('file', self.job_directory, 'get-status', '--sim-id', self.experiment.simulations[0].id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

    def test_status(self):
        result = run_command('file', self.job_directory, 'status', '--exp-id', self.experiment.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

        # for --display
        result = run_command('file', self.job_directory, 'status', '--exp-id', self.experiment.id, '--display')
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

    def test_status_report(self):
        result = run_command('file', self.job_directory, 'status-report', '--exp-id', self.experiment.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        # suite id
        result = run_command('file', self.job_directory, 'status-report', '--suite-id', self.suite.id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)
        # with status-filter option
        result = run_command('file', self.job_directory, 'status-report', '--exp-id', self.experiment.id,
                             '--status-filter', '0')
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

        # with display-count option
        result = run_command('file', self.job_directory, 'status-report', '--exp-id', self.experiment.id,
                             '--display-count', 3)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

        # sim-filter option
        result = run_command('file', self.job_directory, 'status-report', '--exp-id', self.experiment.id,
                             '--sim-filter', self.experiment.simulations[0].id)
        self.assertTrue(result.exit_code == 0, msg=result.output)
        print(result.stdout)

