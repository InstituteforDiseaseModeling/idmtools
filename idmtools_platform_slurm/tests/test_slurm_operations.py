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
from idmtools_platform_slurm.slurm_operations.slurm_operations import SlurmOperations
from idmtools_platform_slurm.slurm_platform import SlurmPlatform
from idmtools_test.utils.decorators import linux_only

from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools_test.utils.test_task import TestTask

job_dir = os.path.expanduser('~')

slurm_vars = [
    'SLURM_JOB_ID', 'SLURM_CPU_BIND', 'SLURM_CPU_BIND_TYPE',
    'SLURM_JOB_NODELIST', 'SLURM_NODELIST', 'SLURM_NNODES',
    'SLURM_NTASKS', 'SLURM_TASKS_PER_NODE', 'SLURM_MEM_PER_CPU',
    'SLURM_MEM_PER_NODE',
]

@pytest.mark.smoke
@pytest.mark.serial
class TestSlurmOperations(ITestWithPersistence):

    def setUp(self) -> None:
        self.platform = Platform('SLURM_LOCAL')

    def _generate_batch_from_simtools_config(self, extra_config_lines=None):
        """Create a batch file using a temporary simtools.ini and return its contents."""
        original_config = os.environ.get("IDMTOOLS_CONFIG_FILE")
        IdmConfigParser.clear_instance()
        contents = None
        with tempfile.TemporaryDirectory() as temp_dir:
            job_dir = os.path.join(temp_dir, "jobs")
            os.makedirs(job_dir, exist_ok=True)
            simtools_ini = os.path.join(temp_dir, "simtools.ini")
            config_lines = [
                "[SLURM_SIMTOOLS]",
                "type = Slurm",
                f"job_directory = {job_dir}",
            ]
            if extra_config_lines:
                config_lines.extend(extra_config_lines)
            with open(simtools_ini, "w") as config_file:
                config_file.write("\n".join(config_lines))
            os.environ["IDMTOOLS_CONFIG_FILE"] = simtools_ini
            IdmConfigParser.clear_instance()
            try:
                platform = Platform('SLURM_SIMTOOLS')
                slurm_op = SlurmOperations(platform=platform)
                suite = Suite(name="Suite")
                experiment = Experiment(name="ExpSimtools")
                experiment.parent = suite
                slurm_op.mk_directory(experiment)
                slurm_op.create_batch_file(experiment)
                batch_path = os.path.join(platform.get_directory(experiment), "batch.sh")
                self.assertTrue(os.path.exists(batch_path))
                with open(batch_path, 'r') as batch_file:
                    contents = batch_file.read()
            finally:
                IdmConfigParser.clear_instance()
                if original_config is None:
                    os.environ.pop("IDMTOOLS_CONFIG_FILE", None)
                else:
                    os.environ["IDMTOOLS_CONFIG_FILE"] = original_config
        return contents

    # Test platform slurm_fields property
    def test_slurm_platform_fields(self):
        actual_field_set = self.platform.slurm_fields
        expected_field_set = {'mem', 'partition', 'time', 'requeue', 'mail_user', 'ntasks', 'modules',
                              'exclusive', 'mail_type', 'sbatch_custom', 'nodes', 'ntasks_per_core', 'account',
                              'mem_per_cpu', 'max_running_jobs', 'cpus_per_task', 'constraint', 'mpi_type'}

        self.assertEqual(set(expected_field_set), set(actual_field_set))

    # Test platform get_slurm_configs with default config
    def test_slurm_configs_default(self):
        slurm_configs_dict = self.platform.get_slurm_configs()
        expected_config_dict = {'mem': None, 'time': None, 'modules': [], 'mail_user': None,
                                'exclusive': False, 'sbatch_custom': None, 'nodes': None, 'mail_type': None,
                                'partition': None, 'account': None, 'ntasks_per_core': None, 'requeue': True,
                                'max_running_jobs': None, 'mem_per_cpu': None, 'ntasks': None, 'cpus_per_task': None,
                                'constraint': None, 'mpi_type': 'pmi2'}

        self.assertEqual(set(slurm_configs_dict), set(expected_config_dict))

    # Test platform get_slurm_configs with user defined configs
    def test_slurm_configs_from_user_defined(self):
        IdmConfigParser.clear_instance()
        platform = Platform("SLURM_TEST", job_directory=".",  mail_user="test@test.com",
                            account="test_acct", mail_type="begin", mem_per_cpu=2048)
        slurm_configs_dict = platform.get_slurm_configs()
        expected_config_dict = {'account': 'test_acct', 'exclusive': False, 'mail_type': 'begin',
                                'mail_user': 'test@test.com', 'max_running_jobs': None, 'mem': None,
                                'mem_per_cpu': 2048, 'modules': [], 'nodes': None, 'ntasks': None,
                                'ntasks_per_core': None, 'partition': None, 'requeue': True,
                                'sbatch_custom': None, 'time': None, 'cpus_per_task': None, 'constraint': None,
                                'mpi_type': 'pmi2'}

        self.assertEqual(set(slurm_configs_dict), set(expected_config_dict))

        # validate custom default config get override with Platform parameters
        self.assertEqual(platform.job_directory, os.getcwd())
        self.assertTrue(isinstance(platform, SlurmPlatform))

    # Test SlurmOperations get_directory for suite only case
    def test_SlurmOperations_get_directory_suite(self):
        suite = Suite(name="Suite")
        slurm_op = SlurmOperations(platform=self.platform)
        actual_entity_path = slurm_op.get_directory(suite)
        suite_dir = str(self.platform.get_directory(suite))
        self.assertEqual(str(actual_entity_path), suite_dir)

    # Test SlurmOperations get_directory for multiple experiments case
    def test_SlurmOperations_get_directory_experiments(self):
        suite = Suite(name="Suite")
        exp1 = Experiment(name="Exp1")
        exp1.parent = suite
        exp2 = Experiment(name="Exp2")
        exp2.parent = suite
        exp3 = Experiment(name="Exp3")
        exp3.parent = suite
        exp_dir1 = str(self.platform.get_directory(exp1))
        suite_dir = str(self.platform.get_directory(suite))
        slurm_op = SlurmOperations(platform=self.platform)
        actual_suite_path = slurm_op.get_directory(suite)
        self.assertEqual(str(actual_suite_path), suite_dir)

        actual_exp1_path = slurm_op.get_directory(exp1)
        self.assertEqual(str(actual_exp1_path), exp_dir1)

    # Test SlurmOperations get_directory for experiment only
    def test__SlurmOperations_get_directory_experiment_no_suite(self):
        exp = Experiment(name="Exp1")
        slurm_op = SlurmOperations(platform=self.platform)
        actual_entity_path = slurm_op.get_directory(exp)
        self.assertEqual(f"e_Exp1_{exp.id}", actual_entity_path.name)

    # Test SlurmOperations get_directory for simulation and experiment as parent
    def test_SlurmOperations_get_directory_simulation(self):
        suite = Suite(name="Suite")
        experiment = Experiment(name="Exp1")
        experiment.parent = suite
        simulation = Simulation()
        simulation.parent = experiment
        slurm_op = SlurmOperations(platform=self.platform)
        actual_entity_path = slurm_op.get_directory(simulation)
        sim_dir = str(self.platform.get_directory(simulation))
        self.assertEqual(str(actual_entity_path), sim_dir)

    # Test SlurmOperations get_directory for simulation without parent, it should throw error
    def test_SlurmOperations_get_simulation_no_experiment_entity_dir(self):
        simulation = Simulation(name="Sim1")
        slurm_op = SlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            actual_entity_path = slurm_op.get_directory(simulation)
        self.assertEqual(ex.exception.args[0], "Simulation missing parent!")

    # Test SlurmOperations mk_directory with suite and without dest
    def test_SlurmOperations_make_dir_no_dest_suite(self):
        suite = Suite(name="Suite")
        suite_dir = str(self.platform.get_directory(suite))
        slurm_op = SlurmOperations(platform=self.platform)
        slurm_op.mk_directory(suite)
        self.assertTrue(os.path.isdir(suite_dir))
        # delete dir after test
        shutil.rmtree(suite_dir)
        self.assertFalse(os.path.isdir(suite_dir))

    # Test SlurmOperations mk_directory with dest
    def test_SlurmOperations_make_dir_dest_suite(self):
        suite = Suite(name="Suite")
        slurm_op = SlurmOperations(platform=self.platform)
        dest_dir = tempfile.mkdtemp()
        slurm_op.mk_directory(suite, dest=dest_dir, exist_ok=True)
        expected_dir = os.path.join(dest_dir)
        self.assertTrue(os.path.isdir(expected_dir))

        # make sure we do not create suite id folder under dest folder in this case
        self.assertFalse(os.path.isdir(os.path.join(dest_dir, suite.id)))

    # Test SlurmOperations mk_directory without entity and dest
    def test_SlurmOperations_make_dir_no_params(self):
        slurm_op = SlurmOperations(platform=self.platform)
        with self.assertRaises(RuntimeError) as ex:
            slurm_op.mk_directory()
        self.assertEqual(ex.exception.args[0], "Only support Suite/Experiment/Simulation or not None dest.")

    # Test SlurmOperations mk_directory for simulation
    def test_SlurmOperations_make_dir_dest_simulations(self):
        slurm_op = SlurmOperations(platform=self.platform)
        suite = Suite(name="Suite")
        experiment = Experiment(name="Exp1")
        experiment.parent = suite
        simulation1 = Simulation(name="Sim1")  # create uniq simulation
        simulation2 = Simulation(name="Sim2")
        simulation1.parent = experiment
        simulation2.parent = experiment
        slurm_op.mk_directory(simulation1)
        slurm_op.mk_directory(simulation2)
        suite_dir = str(self.platform.get_directory(suite))
        sim_dir1 = str(self.platform.get_directory(simulation1))
        sim_dir2 = str(self.platform.get_directory(simulation2))
        self.assertTrue(os.path.isdir(sim_dir1))
        self.assertTrue(os.path.isdir(sim_dir2))
        # delete dir after test
        shutil.rmtree(sim_dir1)
        shutil.rmtree(sim_dir2)
        self.assertFalse(os.path.isdir(sim_dir1))
        self.assertFalse(os.path.isdir(sim_dir2))

    # Test SlurmOperations create_batch_file for experiment
    def test_SlurmOperations_create_batch_file_experiment(self):
        slurm_op = SlurmOperations(platform=self.platform)
        suite = Suite(name="Suite")
        experiment = Experiment(name="Exp1")
        experiment.parent = suite
        exp_dir = str(self.platform.get_directory(experiment))
        suite_dir = str(self.platform.get_directory(suite))
        slurm_op.mk_directory(experiment)
        slurm_op.create_batch_file(experiment)
        # verify batch file locally
        job_path = os.path.join(exp_dir, "sbatch.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation sbatch.sh content
        with open(job_path) as f:
            contents = f.read()
        # check srun run_simulation.sh in sbatch.sh file
        self.assertIn(
            "bash run_simulation.sh",
            contents)
        # clean up suite folder
        shutil.rmtree(exp_dir)
        self.assertFalse(os.path.exists(job_path))

    def _generate_batch_for_platform(self, platform):
        """Generate batch.sh for a given platform instance and return its contents."""
        slurm_op = SlurmOperations(platform=platform)
        suite = Suite(name="Suite")
        experiment = Experiment(name="PropagateTest")
        experiment.parent = suite
        slurm_op.mk_directory(experiment)
        slurm_op.create_batch_file(experiment)
        batch_path = platform.get_directory(experiment).joinpath("batch.sh")
        self.assertTrue(batch_path.exists(), "batch.sh was not created")
        with open(batch_path, 'r') as f:
            return f.read()

    # Tests for propagate_slurm_env_var field definition
    def test_propagate_slurm_env_var_field_default_is_true_and_meta(self):
        """Test that the propagate_slurm_env_var field defaults to True."""
        from dataclasses import fields as dc_fields
        field_map = {f.name: f for f in dc_fields(SlurmPlatform)}
        self.assertIn('propagate_slurm_env_var', field_map)
        self.assertTrue(field_map['propagate_slurm_env_var'].default)
        meta = field_map['propagate_slurm_env_var'].metadata
        self.assertIn('sbatch', meta)
        self.assertFalse(meta['sbatch'])

    def test_propagate_slurm_env_var_excluded_from_slurm_fields(self):
        """Test that propagate_slurm_env_var is not exposed as an sbatch parameter."""
        self.assertNotIn('propagate_slurm_env_var', self.platform.slurm_fields)

    # Tests for propagate_slurm_env_var platform instantiation
    def test_propagate_slurm_env_var_default_value_on_platform(self):
        """Test that platform instance has propagate_slurm_env_var=True by default."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir)
                self.assertTrue(platform.propagate_slurm_env_var)
            finally:
                IdmConfigParser.clear_instance()

    def test_propagate_slurm_env_var_false_via_constructor(self):
        """Test that propagate_slurm_env_var=False passed via constructor is retained."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir,
                                    propagate_slurm_env_var=False)
                self.assertFalse(platform.propagate_slurm_env_var)
            finally:
                IdmConfigParser.clear_instance()

    def test_propagate_slurm_env_var_true_via_constructor(self):
        """Test that propagate_slurm_env_var=True passed via constructor is retained."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir,
                                    propagate_slurm_env_var=True)
                self.assertTrue(platform.propagate_slurm_env_var)
            finally:
                IdmConfigParser.clear_instance()

    # Tests for propagate_slurm_env_var effect on batch.sh content
    def test_propagate_slurm_env_var_false_adds_unset_block_to_batch(self):
        """Test that propagate_slurm_env_var=False produces unset commands in batch.sh."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir)
                platform.propagate_slurm_env_var = False
                contents = self._generate_batch_for_platform(platform)
            finally:
                IdmConfigParser.clear_instance()
        self.assertIn("unset SLURM_JOB_ID", contents)
        self.assertIn("unset SLURM_MEM_PER_NODE", contents)

    def test_propagate_slurm_env_var_true_omits_unset_block_from_batch(self):
        """Test that propagate_slurm_env_var=True excludes unset commands from batch.sh."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir)
                platform.propagate_slurm_env_var = True
                contents = self._generate_batch_for_platform(platform)
            finally:
                IdmConfigParser.clear_instance()
        self.assertNotIn("unset SLURM_JOB_ID", contents)
        self.assertNotIn("unset SLURM_MEM_PER_NODE", contents)

    def test_propagate_slurm_env_var_false_unsets_all_slurm_env_vars(self):
        """Test that all expected SLURM env vars appear in the unset block when False."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir)
                platform.propagate_slurm_env_var = False
                contents = self._generate_batch_for_platform(platform)
            finally:
                IdmConfigParser.clear_instance()
        for var in slurm_vars:
            self.assertIn(f"unset {var}", contents,
                          f"Expected 'unset {var}' in batch.sh when propagate_slurm_env_var=False")

    def test_propagate_slurm_env_var_true_keeps_all_slurm_env_vars(self):
        """Test that no SLURM env vars are unset in batch.sh when propagate_slurm_env_var=True."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir)
                platform.propagate_slurm_env_var = True
                contents = self._generate_batch_for_platform(platform)
            finally:
                IdmConfigParser.clear_instance()
        for var in slurm_vars:
            self.assertNotIn(f"unset {var}", contents,
                             f"Unexpected 'unset {var}' in batch.sh when propagate_slurm_env_var=True")

    def test_propagate_slurm_env_var_false_via_constructor_generates_unset_block(self):
        """End-to-end: propagate_slurm_env_var=False via constructor produces unset block."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir,
                                    propagate_slurm_env_var=False)
                contents = self._generate_batch_for_platform(platform)
            finally:
                IdmConfigParser.clear_instance()
        for var in slurm_vars:
            self.assertIn(f"unset {var}", contents,
                          f"Expected 'unset {var}' in batch.sh when propagate_slurm_env_var=False")

    def test_propagate_slurm_env_var_true_via_constructor_omits_unset_block(self):
        """End-to-end: propagate_slurm_env_var=True via constructor omits unset block."""
        IdmConfigParser.clear_instance()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                platform = Platform("SLURM_TEST", job_directory=temp_dir,
                                    propagate_slurm_env_var=True)
                contents = self._generate_batch_for_platform(platform)
            finally:
                IdmConfigParser.clear_instance()
        for var in slurm_vars:
            self.assertNotIn(f"unset {var}", contents,
                             f"Unexpected 'unset {var}' in batch.sh when propagate_slurm_env_var=True")

    def test_simtools_ini_propagate_slurm_env_var_updates_batch_script(self):
        contents = self._generate_batch_from_simtools_config([
            "propagate_slurm_env_var = False"
        ])
        for var in slurm_vars:
            self.assertIn(f"unset {var}", contents,
                          f"Expected 'unset {var}' in batch.sh when propagate_slurm_env_var=False")

    def test_simtools_ini_propagate_true_or_default_keeps_slurm_env_vars(self):
        scenarios = {
            "explicit_true": ["propagate_slurm_env_var = True"],
            "unspecified": None,
        }
        for name, extra_lines in scenarios.items():
            with self.subTest(case=name):
                contents = self._generate_batch_from_simtools_config(extra_lines)
                self.assertNotIn("unset SLURM_JOB_ID", contents)
                self.assertNotIn("unset SLURM_MEM_PER_NODE", contents)

    def test_legacy_propagate_key_still_supported(self):
        contents = self._generate_batch_from_simtools_config([
            "propagate_slurm_env_var = False"
        ])
        for var in slurm_vars:
            self.assertIn(f"unset {var}", contents,
                          f"Expected 'unset {var}' in batch.sh when propagate_slurm_env_var=False")

    # Test SlurmOperations create_batch_file for simulation
    def test_SlurmOperations_create_batch_file_simulation(self):
        slurm_op = SlurmOperations(platform=self.platform)
        suite = Suite(name="Suite")
        experiment = Experiment(name="Exp1")
        experiment.parent = suite
        simulation = Simulation(task=TestTask())
        simulation.parent = experiment
        suite_dir = str(self.platform.get_directory(suite))
        exp_dir = str(self.platform.get_directory(experiment))
        simulation_dir = str(self.platform.get_directory(simulation))
        slurm_op.mk_directory(simulation)
        slurm_op.create_batch_file(simulation)
        # verify batch file
        job_path = os.path.join(simulation_dir, "_run.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation _run.sh content
        shutil.rmtree(exp_dir)
        self.assertFalse(os.path.exists(job_path))

    # Test SlurmOperations create_batch_file with simulation
    def test_SlurmOperations_create_batch_file_simulation_and_item_path(self):
        slurm_op = SlurmOperations(platform=self.platform)
        suite = Suite(name="Suite")
        experiment = Experiment(name="Exp1")
        experiment.parent = suite
        slurm_op.mk_directory(experiment)
        slurm_op.create_batch_file(experiment)
        simulation = Simulation(task=TestTask())
        simulation.parent = experiment
        slurm_op.mk_directory(simulation)
        slurm_op.create_batch_file(simulation)
        # verify batch file
        job_path = self.platform.get_directory(simulation).joinpath("_run.sh")
        self.assertTrue(os.path.exists(job_path))
        # TODO validation _run.sh content

    # Test SlurmOperations create_batch_file with suite. this case will throw error
    def test_SlurmOperations_create_batch_file_simulation_and_item_path1(self):
        slurm_op = SlurmOperations(platform=self.platform)
        suite = Suite(name="Suite")
        temp_path = tempfile.mkdtemp()
        slurm_op.mk_directory(suite, dest=temp_path, exist_ok=True)
        with self.assertRaises(NotImplementedError) as ex:
            slurm_op.create_batch_file(suite, item_path=temp_path)
        self.assertEqual(ex.exception.args[0], "Suite is not supported for batch creation.")

    @linux_only
    def test_SlurmOperations_link_file(self):
        slurm_op = SlurmOperations(platform=self.platform)
        temp_source_path = tempfile.mkdtemp()
        temp_dest_path = tempfile.mkdtemp()
        target_file = "test.txt"
        with open(os.path.join(temp_source_path, target_file), 'w') as fp:
            fp.write("this is test file")

        # First test with filepath for target and link
        slurm_op.link_file(target=os.path.join(temp_source_path, target_file),
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
        slurm_op.link_file(target=temp_source_path + "/" + target_file, link=temp_dest_path + "/" + target_file)
        self.assertTrue(os.path.exists(os.path.join(temp_dest_path, target_file)))
        with open(os.path.join(temp_dest_path, target_file), 'r') as fpr:
            contents = fpr.read()
        self.assertEqual(contents, "this is test file1")

    @linux_only
    def test_SlurmOperations_link_dir(self):
        slurm_op = SlurmOperations(platform=self.platform)
        temp_source_path = tempfile.mkdtemp()
        dest_path = "DEST_TEST"
        target_file = "test.txt"
        with open(os.path.join(temp_source_path, target_file), 'w') as fp:
            fp.write("this is test file")
        slurm_op.link_dir(target=temp_source_path, link=dest_path)
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
