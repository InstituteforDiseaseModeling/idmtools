import os
import shutil
import tempfile
from uuid import UUID, uuid4

import pytest

from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations import LocalSlurmOperations

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence

cwd = os.path.dirname(__file__)

@pytest.mark.smoke
class TestPythonSimulation(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('SLURM_LOCAL')

    def test_slurm_platform_fields(self):
        actual_field_set = self.platform.slurm_fields
        expected_field_set = {'notification_email', 'memory_per_cpu', 'cpu_per_task', 'requeue', 'mail_type',
                              'exclusive', 'nodes', 'account', 'ntasks', 'modules', 'partition', 'mail_user',
                              'time_limit'}
        self.assertEqual(sorted(expected_field_set), sorted(actual_field_set))

    def test_slurm_slurm_configs(self):
        slurm_configs_dict = self.platform.get_slurm_configs()
        expected_config_dict = {'mail_user': None, 'account': None, 'exclusive': False, 'ntasks': 1,
                                'partition': 'cpu_short', 'memory_per_cpu': 8192, 'modules': [], 'mail_type': None,
                                'time_limit': None, 'notification_email': None, 'requeue': False, 'cpu_per_task': 1,
                                'nodes': 1}
        self.assertEqual(slurm_configs_dict, expected_config_dict)

    # suite only case
    def test_localSlurmOperations_get_suite_entity_dir(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_entity_dir(suite)
        expected_path = os.path.join(cwd, suite.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # one experiment case
    def test_localSlurmOperations_get_experiment_entity_dir(self):
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_entity_dir(experiment)
        expected_path = os.path.join(cwd, suite.id, experiment.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # multiple experiments case
    def test_localSlurmOperations_get_experiments_entity_dir(self):
        suite = Suite()
        exp1 = Experiment()
        exp1.parent = suite
        exp2 = Experiment()
        exp2.parent = suite
        exp3 = Experiment()
        exp3.parent = suite
        local = LocalSlurmOperations(platform=self.platform)
        actual_suite_path = local.get_entity_dir(suite)
        expected_suite_path = os.path.join(cwd, suite.id)
        self.assertEqual(str(actual_suite_path), expected_suite_path)

        actual_exp1_path = local.get_entity_dir(exp1)
        expected_exp1_path = os.path.join(cwd, suite.id, exp1.id)
        self.assertEqual(str(actual_exp1_path), expected_exp1_path)

    # experiment without parent, it should throw error
    def test__localSlurmOperations_get_experiment_no_suite_entity_dir(self):
        exp = Experiment()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_entity_dir(exp)
        self.assertEqual(ex.exception.args[0], "Experiment missing parent!")

    # simulation case
    def test_localSlurmOperations_get_simulation_entity_dir(self):
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        simulation = Simulation()
        simulation.parent = experiment
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_entity_dir(simulation)
        expected_path = os.path.join(cwd, suite.id, experiment.id, simulation.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # simulation without parent, it should throw error
    def test_localSlurmOperations_get_simulation_no_experiment_entity_dir(self):
        simulation = Simulation()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_entity_dir(simulation)
        self.assertEqual(ex.exception.args[0], "Simulation missing parent!")

    # create dir if no dest defined
    def test_localSlurmOperations_make_dir_no_dest_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        local.mk_directory(suite)
        expected_dir = os.path.join(cwd, suite.id)
        self.assertTrue(os.path.isdir(expected_dir))
        # delete dir after test
        shutil.rmtree(expected_dir)
        self.assertFalse(os.path.isdir(expected_dir))

    # create dir with dest defined
    def test_localSlurmOperations_make_dir_dest_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        dest_dir = tempfile.mkdtemp()
        local.mk_directory(suite, dest=dest_dir)
        expected_dir = os.path.join(dest_dir)
        self.assertTrue(os.path.isdir(expected_dir))

        # make sure we do not create suite id folder under dest folder in this case
        self.assertFalse(os.path.isdir(os.path.join(dest_dir, suite.id)))

    # test mk_directory method without pass item and dest parameters
    def test_localSlurmOperations_make_dir_no_params(self):
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            local.mk_directory()
        self.assertEqual(ex.exception.args[0], "Only support Suite/Experiment/Simulation or not None dest.")

    # create dirs for suite/experiment/simulations
    def test_localSlurmOperations_make_dir_dest_suite(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        simulation1 = Simulation(_uid=uuid4())  # create uniq simulation
        simulation2 = Simulation(_uid=uuid4())
        simulation1.parent = experiment
        simulation2.parent = experiment
        local.mk_directory(simulation1)
        local.mk_directory(simulation2)
        expected_dir1 = os.path.join(cwd, suite.id, experiment.id, simulation1.id)
        expected_dir2 = os.path.join(cwd, suite.id, experiment.id, simulation2.id)
        self.assertTrue(os.path.isdir(expected_dir1))
        self.assertTrue(os.path.isdir(expected_dir2))
        # delete dir after test
        shutil.rmtree(expected_dir1)
        self.assertFalse(os.path.isdir(expected_dir1))
        shutil.rmtree(expected_dir2)
        self.assertFalse(os.path.isdir(expected_dir2))
