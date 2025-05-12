import os
import pytest
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_test.utils.decorators import linux_only
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


@pytest.mark.serial
@linux_only
class TestSingularity(ITestWithPersistence):

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        self.job_directory = "DEST"
        self.platform = Platform('FILE', job_directory=self.job_directory)

    def test_command_build_singularity(self):
        command = "singularity exec my.sif Assets/hello.sh"
        task = CommandTask(command=command)
        task.common_assets.add_asset("input/hello.sh")

        # create experiment from task
        experiment = Experiment.from_task(task, name="run_task_in_singularity")
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False)
        for simulation in experiment.simulations:
            simulation_dir = self.platform.get_directory(simulation)
            exe = simulation_dir.joinpath("Assets/hello.sh")
            self.assertTrue(os.access(exe, os.X_OK))
            with open(os.path.join(simulation_dir, '_run.sh'), 'r') as fpr:
                contents = fpr.read()
            self.assertIn(command, contents)

    # To test command line with extra command option for singularity case in _run.sh for each simulation
    # note, we do not need to test run successfully, since we do not have actually sif file to test
    def test_extra_command_build_singularity(self):
        command = "Assets/hello.sh"  # assume hello.sh is our executable
        task = CommandTask(command=command)
        task.sif_path = "my_sif.sif"
        task.common_assets.add_asset("input/hello.sh")
        task.command._options.update({"--python-script-path": "./Assets/python"})

        # create experiment from task
        experiment = Experiment.from_task(task, name="run_task_in_singularity")
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False)
        for simulation in experiment.simulations:
            simulation_dir = self.platform.get_directory(simulation)
            exe = simulation_dir.joinpath(command)
            self.assertTrue(os.access(exe, os.X_OK))
            with open(os.path.join(simulation_dir, '_run.sh'), 'r') as fpr:
                contents = fpr.read()
            self.assertIn("singularity exec " + task.sif_path + "  " + command + " --python-script-path ./Assets/python", contents)
