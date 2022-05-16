import os
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations import LocalSlurmOperations

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


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
        cwd = os.path.dirname(__file__)
        expected_path = os.path.join(cwd, suite.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # one experiment case
    def test_localSlurmOperations_get_experiment_entity_dir(self):
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_entity_dir(experiment)
        cwd = os.path.dirname(__file__)
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
        cwd = os.path.dirname(__file__)
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
        cwd = os.path.dirname(__file__)
        expected_path = os.path.join(cwd, suite.id, experiment.id, simulation.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # simulation without parent, it should throw error
    def test_localSlurmOperations_get_simulation_no_experiment_entity_dir(self):
        simulation = Simulation()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_entity_dir(simulation)
        self.assertEqual(ex.exception.args[0], "Simulation missing parent!")

