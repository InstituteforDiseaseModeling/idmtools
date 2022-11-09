import os
import pathlib
import shutil
import tempfile
import pytest

from idmtools import IdmConfigParser
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_slurm.slurm_operations.local_operations import LocalSlurmOperations
from idmtools_test.utils.decorators import linux_only

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

job_dir = os.path.expanduser('~')


@pytest.mark.smoke
@pytest.mark.serial
class TestSlurmPlatform(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('SLURM_LOCAL')

    # Test platform slurm_fields property
    def test_slurm_platform_fields(self):
        actual_field_set = self.platform.slurm_fields
        expected_field_set = {'mem', 'partition', 'time', 'requeue', 'mail_user', 'ntasks', 'modules',
                              'exclusive', 'mail_type', 'sbatch_custom', 'nodes', 'ntasks_per_core', 'account',
                              'mem_per_cpu', 'max_running_jobs', 'cpus_per_task'}

        self.assertEqual(set(expected_field_set), set(actual_field_set))

    # Test platform get_slurm_configs with default config
    def test_slurm_configs_default(self):
        slurm_configs_dict = self.platform.get_slurm_configs()
        expected_config_dict = {'mem': None, 'time': None, 'modules': [], 'mail_user': None,
                                'exclusive': False, 'sbatch_custom': None, 'nodes': None, 'mail_type': None,
                                'partition': None, 'account': None, 'ntasks_per_core': None, 'requeue': True,
                                'max_running_jobs': None, 'mem_per_cpu': None, 'ntasks': None, 'cpus_per_task': None}

        self.assertEqual(set(slurm_configs_dict), set(expected_config_dict))

    # Test platform get_slurm_configs with user defined configs
    def test_slurm_configs_from_user_defined(self):
        IdmConfigParser.clear_instance()
        platform = Platform("SLURM_TEST", job_directory=".", mode="local", mail_user="test@test.com",
                            account="test_acct", mail_type="begin", mem_per_cpu=2048)
        slurm_configs_dict = platform.get_slurm_configs()
        expected_config_dict = {'account': 'test_acct', 'exclusive': False, 'mail_type': 'begin',
                                'mail_user': 'test@test.com', 'max_running_jobs': None, 'mem': None,
                                'mem_per_cpu': 2048, 'modules': [], 'nodes': None, 'ntasks': None,
                                'ntasks_per_core': None, 'partition': None, 'requeue': True,
                                'sbatch_custom': None, 'time': None, 'cpus_per_task': None}

        self.assertEqual(set(slurm_configs_dict), set(expected_config_dict))

        # validate custom default config get override with Platform parameters
        self.assertEqual(platform.job_directory, '.')
        self.assertEqual(platform.mode.name, "LOCAL")
        self.assertEqual(platform.mode.value, "local")

    # Test LocalSlurmOperations get_directory for suite only case
    def test_localSlurmOperations_get_directory_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_directory(suite)
        expected_path = os.path.join(job_dir, suite.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # Test LocalSlurmOperations get_directory for multiple experiments case
    def test_localSlurmOperations_get_directory_experiments(self):
        suite = Suite()
        exp1 = Experiment()
        exp1.parent = suite
        exp2 = Experiment()
        exp2.parent = suite
        exp3 = Experiment()
        exp3.parent = suite
        local = LocalSlurmOperations(platform=self.platform)
        actual_suite_path = local.get_directory(suite)
        expected_suite_path = os.path.join(job_dir, suite.id)
        self.assertEqual(str(actual_suite_path), expected_suite_path)

        actual_exp1_path = local.get_directory(exp1)
        expected_exp1_path = os.path.join(job_dir, suite.id, exp1.id)
        self.assertEqual(str(actual_exp1_path), expected_exp1_path)

    # Test LocalSlurmOperations get_directory for experiment only
    def test__localSlurmOperations_get_directory_experiment_no_suite(self):
        exp = Experiment()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_directory(exp)
        self.assertEqual(ex.exception.args[0], "Experiment missing parent!")

    # Test LocalSlurmOperations get_directory for simulation and experiment as parent
    def test_localSlurmOperations_get_directory_simulation(self):
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        simulation = Simulation()
        simulation.parent = experiment
        local = LocalSlurmOperations(platform=self.platform)
        actual_entity_path = local.get_directory(simulation)
        expected_path = os.path.join(job_dir, suite.id, experiment.id, simulation.id)
        self.assertEqual(str(actual_entity_path), expected_path)

    # Test LocalSlurmOperations get_directory for simulation without parent, it should throw error
    def test_localSlurmOperations_get_simulation_no_experiment_entity_dir(self):
        simulation = Simulation()
        local = LocalSlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = local.get_directory(simulation)
        self.assertEqual(ex.exception.args[0], "Simulation missing parent!")

    # Test LocalSlurmOperations mk_directory with suite and without dest
    def test_localSlurmOperations_make_dir_no_dest_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        local.mk_directory(suite)
        expected_dir = os.path.join(job_dir, suite.id)
        self.assertTrue(os.path.isdir(expected_dir))
        # delete dir after test
        shutil.rmtree(expected_dir)
        self.assertFalse(os.path.isdir(expected_dir))

    # Test LocalSlurmOperations mk_directory with dest
    def test_localSlurmOperations_make_dir_dest_suite(self):
        suite = Suite()
        local = LocalSlurmOperations(platform=self.platform)
        dest_dir = tempfile.mkdtemp()
        local.mk_directory(suite, dest=dest_dir, exist_ok=True)
        expected_dir = os.path.join(dest_dir)
        self.assertTrue(os.path.isdir(expected_dir))

        # make sure we do not create suite id folder under dest folder in this case
        self.assertFalse(os.path.isdir(os.path.join(dest_dir, suite.id)))

    # Test LocalSlurmOperations mk_directory without entity and dest
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
        simulation1 = Simulation()  # create uniq simulation
        simulation2 = Simulation()
        simulation1.parent = experiment
        simulation2.parent = experiment
        local.mk_directory(simulation1)
        local.mk_directory(simulation2)
        expected_dir1 = os.path.join(job_dir, suite.id, experiment.id, simulation1.id)
        expected_dir2 = os.path.join(job_dir, suite.id, experiment.id, simulation2.id)
        self.assertTrue(os.path.isdir(expected_dir1))
        self.assertTrue(os.path.isdir(expected_dir2))
        # delete dir after test
        shutil.rmtree(os.path.join(job_dir, suite.id))
        self.assertFalse(os.path.isdir(expected_dir1))
        self.assertFalse(os.path.isdir(expected_dir2))

    # Test LocalSlurmOperations create_batch_file for experiment
    def test_localSlurmOperations_create_batch_file_experiment(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        local.mk_directory(experiment)
        local.create_batch_file(experiment)
        # verify batch file locally
        job_path = os.path.join(job_dir, suite.id, experiment.id, "sbatch.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation sbatch.sh content
        with open(job_path) as f:
            contents = f.read()
        # check srun run_simulation.sh in sbatch.sh file
        self.assertIn(
            "run run_simulation.sh",
            contents)
        # clean up suite folder
        shutil.rmtree(os.path.join(job_dir, suite.id))
        self.assertFalse(os.path.exists(job_path))

    # Test LocalSlurmOperations create_batch_file for simulation
    def test_localSlurmOperations_create_batch_file_simulation(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        simulation = Simulation(task=TestTask())
        simulation.parent = experiment
        local.mk_directory(simulation)
        local.create_batch_file(simulation)
        # verify batch file
        job_path = os.path.join(job_dir, suite.id, experiment.id, simulation.id, "_run.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation _run.sh content
        # clean up suite folder
        shutil.rmtree(os.path.join(job_dir, suite.id))
        self.assertFalse(os.path.exists(job_path))

    # Test LocalSlurmOperations create_batch_file with simulation and item_path
    def test_localSlurmOperations_create_batch_file_simulation_and_item_path(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        experiment = Experiment()
        experiment.parent = suite
        simulation = Simulation(task=TestTask())
        simulation.parent = experiment
        temp_path = tempfile.mkdtemp()
        local.mk_directory(simulation, dest=temp_path)
        local.create_batch_file(simulation, item_path=temp_path)
        # verify batch file
        job_path = os.path.join(temp_path, "_run.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation _run.sh content

    # Test LocalSlurmOperations create_batch_file with suite and item_path. this case will throw error
    def test_localSlurmOperations_create_batch_file_simulation_and_item_path(self):
        local = LocalSlurmOperations(platform=self.platform)
        suite = Suite()
        temp_path = tempfile.mkdtemp()
        local.mk_directory(suite, dest=temp_path, exist_ok=True)
        with self.assertRaises(NotImplementedError) as ex:
            local.create_batch_file(suite, item_path=temp_path)
        self.assertEqual(ex.exception.args[0], "Suite is not supported for batch creation.")

    @linux_only
    def test_localSlurmOperations_link_file(self):
        local = LocalSlurmOperations(platform=self.platform)
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        target_file = "test.txt"
        with open(os.path.join(temp_source_path, target_file), 'w') as fp:
            fp.write("this is test file")

        # First test with filepath for target and link
        local.link_file(target=os.path.join(temp_source_path, target_file),
                        link=os.path.join(temp_dest_path, target_file))
        self.assertTrue(os.path.exists(os.path.join(temp_dest_path, target_file)))
        with open(os.path.join(temp_dest_path, target_file), 'r') as fpr:
            contents = fpr.read()
        self.assertEqual(contents, "this is test file")

        # Second test with filepath as string for target and link path as string
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        with open(os.path.join(temp_source_path, target_file), 'w') as fp:
            fp.write("this is test file1")
        local.link_file(target=temp_source_path + "/" + target_file, link=temp_dest_path + "/" + target_file)
        self.assertTrue(os.path.exists(os.path.join(temp_dest_path, target_file)))
        with open(os.path.join(temp_dest_path, target_file), 'r') as fpr:
            contents = fpr.read()
        self.assertEqual(contents, "this is test file1")

    @linux_only
    def test_localSlurmOperations_link_dir(self):
        local = LocalSlurmOperations(platform=self.platform)
        temp_source_path = tempfile.mkdtemp()
        dest_path = "DEST_TEST"
        target_file = "test.txt"
        with open(os.path.join(temp_source_path, target_file), 'w') as fp:
            fp.write("this is test file")
        local.link_dir(target=temp_source_path, link=dest_path)
        self.assertTrue(os.path.exists(os.path.join(dest_path, target_file)))
        with open(os.path.join(dest_path, target_file), 'r') as fpr:
            contents = fpr.read()
        self.assertEqual(contents, "this is test file")

        # Clean up dest_path dir
        for path in pathlib.Path(dest_path).glob("**/*"):
            if path.is_file():
                path.unlink()
        if os.path.isdir(dest_path):
            pathlib.Path(dest_path).unlink()
