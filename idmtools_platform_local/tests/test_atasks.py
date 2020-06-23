import pytest
from idmtools_test.utils.confg_local_runner_test import config_local_test, patch_db, reset_local_broker
from idmtools_test.utils.decorators import linux_only
from idmtools_platform_local.status import Status
from idmtools_test import COMMON_INPUT_PATH
import os
import shutil
from unittest import TestCase


# These tests are simulating behaviours that normally would occur within the local worker container
# Because of that, they should only be executed on linux


@linux_only
@patch_db
@pytest.mark.local_platform_internals
class TestTasks(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        reset_local_broker()
        cls.local_path = config_local_test()
        # set the db to sqlite lite. Store old value in case it is already set
        cls.old_db_uri = os.getenv('SQLALCHEMY_DATABASE_URI', None)
        os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            reset_local_broker()
            os.environ['SQLALCHEMY_DATABASE_URI'] = cls.old_db_uri
            shutil.rmtree(cls.local_path)
        except Exception:
            pass

    def setUp(self) -> None:
        from idmtools_platform_local.internals.tasks.create_experiment import CreateExperimentTask
        self.experiment_id = CreateExperimentTask.perform(dict(a='b', c='d'), dict())
        print(os.environ["DATA_PATH"])

    def test_create_experiment(self, mock_db):
        """
        Test Create experiment actor
        """

        self.assertIsInstance(self.experiment_id, str)

        # Check that the data directory
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id)))
        # Check for assets
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id, "Assets")))

    def test_create_simulation(self, mock_db):
        """
        Test create simulation actor
        """
        from idmtools_platform_local.internals.tasks.create_simulation import CreateSimulationTask
        new_simulation_id = CreateSimulationTask.perform(self.experiment_id, dict(y="z"), dict())

        # Check that the data directory
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id)))
        # Check for assets
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id, "Assets")))
        # Check for simulation id
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id, new_simulation_id)))

    def test_run_task(self, mock_db):
        """
        Test run task actor
        """
        from idmtools_platform_local.internals.tasks.create_simulation import CreateSimulationTask
        from idmtools_platform_local.internals.tasks.general_task import RunTask
        new_simulation_id = CreateSimulationTask.perform(self.experiment_id, dict(y="z"), dict())

        # Check that the data directory
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id)))
        # Check for assets
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id, "Assets")))
        # Check for simulation id
        self.assertTrue(os.path.exists(os.path.join(self.local_path, self.experiment_id, new_simulation_id)))

        # copy simple model over. Since we are doing low-level testing, let's not use asset management here
        shutil.copy(os.path.join(COMMON_INPUT_PATH, 'python', 'hello_world.py'),
                    os.path.join(self.local_path, self.experiment_id, new_simulation_id))

        status = RunTask.perform("python hello_world.py", self.experiment_id, new_simulation_id)
        self.assertEqual(status, Status.done)
