# flake8: noqa E402
from idmtools_test.utils.confg_local_runner_test import config_local_test
local_path = config_local_test()
from idmtools_test.utils.decorators import linux_only
from idmtools_platform_local.status import Status
from idmtools_test import COMMON_INPUT_PATH
import os
import shutil

from idmtools_platform_local.tasks.create_simulation import CreateSimulationTask
from unittest import TestCase
from idmtools_platform_local.tasks.create_experiement import CreateExperimentTask
from idmtools_platform_local.tasks.run import RunTask

# These tests are simulating behaviours that normally would occur within the local worker container
# Because of that, they should only be executed on linux


@linux_only
class TestTasks(TestCase):

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(local_path)

    def test_create_experiment(self):
        """
        Test Create experiment actor
        """
        new_task_id = CreateExperimentTask.perform(dict(a='b', c='d'), "s")
        print(os.environ["DATA_PATH"])
        self.assertIsInstance(new_task_id, str)

        # Check that the data directory
        self.assertTrue(os.path.exists(os.path.join(local_path, new_task_id)))
        # Check for assets
        self.assertTrue(os.path.exists(os.path.join(local_path, new_task_id, "Assets")))

    def test_create_simulation(self):
        """
        Test create simulation actor
        """
        exp_id = CreateExperimentTask.perform(dict(a='b', c='d'), "s")
        new_simulation_id = CreateSimulationTask.perform(exp_id, dict(y="z"))

        # Check that the data directory
        self.assertTrue(os.path.exists(os.path.join(local_path, exp_id)))
        # Check for assets
        self.assertTrue(os.path.exists(os.path.join(local_path,  exp_id, "Assets")))
        # Check for simulation id
        self.assertTrue(os.path.exists(os.path.join(local_path, exp_id, new_simulation_id)))

    def test_run_task(self):
        """
        Test run task actor
        """
        exp_id = CreateExperimentTask.perform(dict(a='b', c='d'), "s")
        new_simulation_id = CreateSimulationTask.perform(exp_id, dict(y="z"))

        # Check that the data directory
        self.assertTrue(os.path.exists(os.path.join(local_path, exp_id)))
        # Check for assets
        self.assertTrue(os.path.exists(os.path.join(local_path, exp_id, "Assets")))
        # Check for simulation id
        self.assertTrue(os.path.exists(os.path.join(local_path, exp_id, new_simulation_id)))

        # copy simple model over. Since we are doing low-level testing, let's not use asset management here
        shutil.copy(os.path.join(COMMON_INPUT_PATH, 'python', 'hello_world.py'),
                    os.path.join(local_path, exp_id, new_simulation_id))

        status = RunTask.perform("python hello_world.py", exp_id, new_simulation_id)
        self.assertEqual(status, Status.done)

