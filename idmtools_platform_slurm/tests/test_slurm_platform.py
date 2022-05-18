import os
import shutil
import tempfile
from uuid import uuid4

import pytest

from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations import LocalSlurmOperations

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

cwd = os.path.dirname(__file__)


@pytest.mark.smoke
@pytest.mark.serial
class TestSlurmPlatform(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('SLURM_LOCAL')

    # Test platform slurm_fields property
    def test_slurm_platform_fields(self):
        actual_field_set = self.platform.slurm_fields
        expected_field_set = {'mem_per_cpu', 'cpus_per_task', 'requeue', 'mail_type',
                              'exclusive', 'nodes', 'account', 'ntasks', 'modules', 'partition', 'mail_user',
                              'time'}
        self.assertEqual(sorted(expected_field_set), sorted(actual_field_set))

    # Test platform get_slurm_configs with default config
    def test_slurm_configs_default(self):
        slurm_configs_dict = self.platform.get_slurm_configs()
        expected_config_dict = {'mail_user': None, 'account': None, 'exclusive': True, 'ntasks': 1,
                                'partition': 'cpu_short', 'mem_per_cpu': 8192, 'modules': [], 'mail_type': None,
                                'time': None, 'requeue': False, 'cpus_per_task': 1,
                                'nodes': 1}
        self.assertEqual(slurm_configs_dict, expected_config_dict)

    # Test platform get_slurm_configs with user defined configs
    def test_slurm_configs_from_user_defined(self):
        platform = Platform("SLURM_TEST", job_directory=".", mode="local", mail_user="test@test.com",
                            account="test_acct", mail_type="begin", mem_per_cpu=2048, cpus_per_task=2)
        slurm_configs_dict = platform.get_slurm_configs()
        expected_config_dict = {'account': 'test_acct', 'cpus_per_task': 2, 'exclusive': True, 'mail_type': 'begin',
                                'mail_user': 'test@test.com', 'mem_per_cpu': 2048, 'modules': [], 'nodes': 1,
                                'ntasks': 1, 'partition': 'cpu_short', 'requeue': False, 'time': None}
        self.assertEqual(slurm_configs_dict, expected_config_dict)

        # validate custom default config get override with Platform parameters
        self.assertEqual(platform.job_directory, '.')
        self.assertEqual(platform.mode.name, "LOCAL")
        self.assertEqual(platform.mode.value, "local")

    # Test LocalSlurmOperations get_batch_configs method
    def test_localSlurmOperations_get_batch_configs(self):
        local = LocalSlurmOperations(platform=self.platform)
        batch_config = local.get_batch_configs()
        self.assertIn("#SBATCH --ntasks=1", batch_config)
        self.assertIn("#SBATCH --partition=cpu_short", batch_config)
        self.assertIn("#SBATCH --cpus-per-task=1", batch_config)
        self.assertIn("#SBATCH --nodes=1", batch_config)
        self.assertIn("#SBATCH --mem-per-cpu=8192", batch_config)

    # # Test LocalSlurmOperations get_entity_dir for suite only case
    def test_localSlurmOperations_get_suite_entity_dir(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_entity_dir(suite)
        expected_path = os.path.join(cwd, suite.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # Test LocalSlurmOperations get_entity_dir for one experiment and suite as parent case
    def test_localSlurmOperations_get_experiment_entity_dir(self):
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_entity_dir(experiment)
        expected_path = os.path.join(cwd, suite.id, experiment.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # Test LocalSlurmOperations get_entity_dir for multiple experiments case
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

    # Test LocalSlurmOperations get_entity_dir for experiment only
    def test__localSlurmOperations_get_experiment_no_suite_entity_dir(self):
        exp = Experiment()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_entity_dir(exp)
        self.assertEqual(ex.exception.args[0], "Experiment missing parent!")

    # Test LocalSlurmOperations get_entity_dir for simulation and experiment as parent
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

    # Test LocalSlurmOperations get_entity_dir for simulation without parent, it should throw error
    def test_localSlurmOperations_get_simulation_no_experiment_entity_dir(self):
        simulation = Simulation()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_entity_dir(simulation)
        self.assertEqual(ex.exception.args[0], "Simulation missing parent!")

    # Test LocalSlurmOperations mk_directory with suite and without dest
    def test_localSlurmOperations_make_dir_no_dest_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        local.mk_directory(suite)
        expected_dir = os.path.join(cwd, suite.id)
        self.assertTrue(os.path.isdir(expected_dir))
        # delete dir after test
        shutil.rmtree(expected_dir)
        self.assertFalse(os.path.isdir(expected_dir))

    # Test LocalSlurmOperations mk_directory with dest
    def test_localSlurmOperations_make_dir_dest_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        dest_dir = tempfile.mkdtemp()
        local.mk_directory(suite, dest=dest_dir)
        expected_dir = os.path.join(dest_dir)
        self.assertTrue(os.path.isdir(expected_dir))

        # make sure we do not create suite id folder under dest folder in this case
        self.assertFalse(os.path.isdir(os.path.join(dest_dir, suite.id)))

    # Test LocalSlurmOperations mk_directory without pass item and dest
    def test_localSlurmOperations_make_dir_no_params(self):
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            local.mk_directory()
        self.assertEqual(ex.exception.args[0], "Only support Suite/Experiment/Simulation or not None dest.")

    # Test LocalSlurmOperations mk_directory for simulation
    def test_localSlurmOperations_make_dir_dest_simulations(self):
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
        shutil.rmtree(os.path.join(cwd, suite.id))
        self.assertFalse(os.path.isdir(expected_dir1))
        self.assertFalse(os.path.isdir(expected_dir2))

    # Test LocalSlurmOperations create_batch_file for experiment
    def test_localSlurmOperations_experiment_create_batch_file(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        experiment = Experiment(_uid=uuid4())
        experiment.parent = suite
        local.mk_directory(experiment)
        local.create_batch_file(experiment)
        # verify batch file locally
        job_path = os.path.join(cwd, suite.id, experiment.id, "job_submit.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation job_submit.sh content
        # with open(job_path) as f:
        #     contents = f.readlines()
        # # check #SBATCH --job-name=experiment.id in job_submit.sh file.
        # if any("#SBATCH --job-name=" + experiment.id in i for i in contents):
        #     self.assertTrue(1)
        # else:
        #     self.assertFalse(1)
        # clean up suite folder
        shutil.rmtree(os.path.join(cwd, suite.id))
        self.assertFalse(os.path.exists(job_path))

    # Test LocalSlurmOperations create_batch_file for simulation
    def test_localSlurmOperations_simulation_create_batch_file(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        experiment = Experiment(_uid=uuid4())
        experiment.parent = suite
        simulation = Simulation(_uid=uuid4(), task=TestTask())
        simulation.parent = experiment
        local.mk_directory(simulation)
        local.create_batch_file(simulation)
        # verify batch file locally
        job_path = os.path.join(cwd, suite.id, experiment.id, simulation.id, "_run.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation _run.sh content
        # clean up suite folder
        shutil.rmtree(os.path.join(cwd, suite.id))
        self.assertFalse(os.path.exists(job_path))
