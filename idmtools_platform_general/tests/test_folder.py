import os
import shutil
import unittest
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools_test.utils.decorators import linux_only
from idmtools.entities.command_task import CommandTask
cwd = os.path.dirname(__file__)


@pytest.mark.smoke
@pytest.mark.serial
@linux_only
class TestFolder(unittest.TestCase):
    def remove_dir(self):
        if os.path.exists(self.job_directory):
            shutil.rmtree(self.job_directory)

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + '--' + self._testMethodName
        self.job_directory = os.path.join(cwd, 'DEST')
        self.platform = Platform('File', job_directory=self.job_directory)
        command = "Assets/hello.sh"
        self.task = CommandTask(command=command)
        self.task.common_assets.add_asset("input/hello.sh")
        self.remove_dir()

    def verify_dir(self, expected_dir, item):
        exp_dir = self.platform.get_directory(item)
        self.assertEqual(expected_dir.replace("\\", "/"), str(exp_dir).replace("\\", "/"))

    # Test case to verify the experiment directory structure when experiment name has space
    def test_0(self):
        experiment = Experiment.from_task(self.task, name="test 0")
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_0_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special character: '
    def test_1(self):
        experiment = Experiment.from_task(self.task, name="test'1")
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_1_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special character: "
    def test_2(self):
        experiment = Experiment.from_task(self.task, name='test"2')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_2_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special character: :
    def test_3(self):
        experiment = Experiment.from_task(self.task, name='test:3')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_3_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special character: ?
    def test_4(self):
        experiment = Experiment.from_task(self.task, name='test?4')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_4_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: <>
    def test_5(self):
        experiment = Experiment.from_task(self.task, name='test<5>')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_5__{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: ()
    def test_6(self):
        experiment = Experiment.from_task(self.task, name='test(6)')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_6__{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: []
    def test_7(self):
        experiment = Experiment.from_task(self.task, name='test[7]')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_7__{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: *
    def test_8(self):
        experiment = Experiment.from_task(self.task, name='test*8')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_8_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: ?
    def test_9(self):
        experiment = Experiment.from_task(self.task, name='test?9')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_9_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: |
    def test_10(self):
        experiment = Experiment.from_task(self.task, name='test|10')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_10_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: `
    def test_11(self):
        experiment = Experiment.from_task(self.task, name='test`11')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_11_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: ,
    def test_12(self):
        experiment = Experiment.from_task(self.task, name='test,12')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_12_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: $
    def test_13(self):
        experiment = Experiment.from_task(self.task, name='test$13')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_13_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: !
    def test_14(self):
        experiment = Experiment.from_task(self.task, name='test!14')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test_14_{experiment.id}", experiment)

    # Test case to verify the experiment directory structure when experiment name has special characters: \0
    def test_15(self):
        experiment = Experiment.from_task(self.task, name='test15\0')
        experiment.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Suite_{experiment.parent_id}/test15__{experiment.id}", experiment)

    # Test case to verify the suite directory structure when suite name has &
    def test_suite(self):
        experiment = Experiment.from_task(self.task, name="experiment+1")  # note + is valid in experiment name
        suite = Suite(name='Idm&Suite')
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False, dry_run=True)
        self.verify_dir(f"{self.job_directory}/Idm_Suite_{experiment.parent_id}/experiment+1_{experiment.id}", experiment)
