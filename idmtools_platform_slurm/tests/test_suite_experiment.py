import os
import pathlib
import sys
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools_platform_file.platform_operations.utils import add_dummy_suite
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence
from idmtools.entities.command_task import CommandTask
cwd = os.path.dirname(__file__)
sys.path.append(cwd)
from helper import remove_dir, verify_result, get_dirs_and_files, verify_result_experiment


@pytest.mark.smoke
@pytest.mark.serial
@linux_only
class TestSuiteExperiment(ITestWithPersistence):
    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + '--' + self._testMethodName
        self.job_directory = os.path.join(cwd, 'DEST')
        self.platform = Platform('SLURM_LOCAL', job_directory=self.job_directory)
        command = "Assets/hello.sh"
        self.task = CommandTask(command=command)
        self.task.common_assets.add_asset("input/hello.sh")
        remove_dir(self)

    def verify_suite_only_case(self, suite):
        suite_dir = self.platform.get_directory(suite)
        suite_sub_dirs, suite_files = get_dirs_and_files(self, suite_dir)
        self.assertTrue(len(suite_files) == 1)
        self.assertEqual(suite_files[0], pathlib.Path(str(suite_dir) + "/metadata.json"))
        # Verify no sub directory under suite at this point
        self.assertTrue(len(suite_sub_dirs) == 0)

    # Verify no suite needed case, we can directory call experiment.run which will create suite for you
    def test_0(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result_experiment(self, experiment)

    # Case 1,2,3,4 test with suite.add_experiment(experiment)
    # Verify suite.run with new suite
    def test_1(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with new suite
    def test_2(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        suite.add_experiment(experiment)
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify suite.run with existing suite
    def test_3(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        self.platform.create_items(suite)
        # Verify suite folder is created with correct file
        self.verify_suite_only_case(suite)
        experiment = Experiment.from_task(self.task, name="run_task")
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with existing suite,
    def test_4(self):
        suite = Suite(name='Idm Suite')
        # create suite first in folder
        self.platform.create_items(suite)
        self.verify_suite_only_case(suite)
        experiment = Experiment.from_task(self.task, name="run_task")
        suite.add_experiment(experiment)
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Case 5,6,7, 8 test with experiment.suite = suite
    # Verify suite.run with new suite
    def test_5(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.suite = suite
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with new suite
    def test_6(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.suite = suite
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with existing suite
    def test_7(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        self.platform.create_items(suite)
        # create experiment and add suite to experiment and run with experiment
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.suite = suite
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify suite.run with existing suite
    def test_8(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        self.platform.create_items(suite)
        # create experiment and add suite to experiment and run with experiment
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.suite = suite
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Case 9, 10, 11, 12 test with  experiment.parent = suite
    # Verify suite.run with new suite
    def test_9(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.parent = suite
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with new suite
    def test_10(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.parent = suite
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify suite.run with existing suite
    def test_11(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        self.platform.create_items(suite)
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.parent = suite
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with existing suite
    def test_12(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        self.platform.create_items(suite)
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.parent = suite
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # case 13, 14 ,15, 16 test with experiment.parent_id = suite.id
    # Verify experiment.run with existing suite
    def test_13(self):
        # create suite first
        suite = Suite(name='Idm Suite')
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_suite_only_case(suite)
        # add suite.id as experiment.parent_id
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.parent_id = suite.id
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with suite not existing yet
    def test_14(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.parent_id = suite.id
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_suite_only_case(suite)

    # Verify experiment.run with existing suite
    def test_15(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_suite_only_case(suite)
        # add suite.id as experiment.parent_id
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.parent_id = suite.id
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify experiment.run with suite not existing yet, it will throw RunTimeError
    def test_16(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.parent_id = suite.id
        with self.assertRaises(RuntimeError) as ex:
            experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.assertEqual(ex.exception.args[0], f"Not found Suite with id '{suite.id}'")

    # Case 17, 18 test with experiment.suite_id = suite.id
    # Verify experiment.run with existing suite.id
    def test_17(self):
        # create suite first in folder
        suite = Suite(name='Idm Suite')
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.suite_id = suite.id  # this only works with existing suite (i.e after run)
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify suite.run with non-existing suite, this case only create suite
    def test_18(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = Suite(name='Idm Suite')
        experiment.suite_id = suite.id
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_suite_only_case(suite)

    # Case 19, 20 test with add_dummy_suite method
    # Verify create dummy suite first, then run suite.run
    def test_19(self):
        exp = Experiment.from_task(self.task, name="run_task")
        suite = add_dummy_suite(exp)
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify create dummy suite first, then run experiment.run
    def test_20(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = add_dummy_suite(experiment)
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    # Verify create experiment only
    def test_21(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        self.platform.run_items(items=experiment, wait_until_done=False, dry_run=True)
        verify_result_experiment(self, experiment)

    # Verify create suite/experiment with platform.run_items(suite)
    def test_22(self):
        experiment = Experiment.from_task(self.task, name="run_task")
        suite = add_dummy_suite(experiment)
        self.platform.run_items(items=suite, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

    def test_23(self):
        # create suite first without name
        suite = Suite()
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_suite_only_case(suite)
        # add suite.id as experiment.parent_id
        experiment = Experiment.from_task(self.task, name="run_task")
        experiment.parent_id = suite.id
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        verify_result(self, suite)

