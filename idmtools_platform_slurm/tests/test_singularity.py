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
        self.platform = Platform('SLURM_LOCAL', job_directory=self.job_directory)

    def testExecutableMode(self):
        command = "Assets/hello.sh"
        task = CommandTask(command=command)
        task.common_assets.add_asset("input/hello.sh")

        # create experiment from task
        experiment = Experiment.from_task(task, name="run_task")
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False, wait_on_done=False,
                  max_running_jobs=10,
                  retries=5, dry_run=True)
        for simulation in experiment.simulations:
            simulation_dir = self.platform._op_client.get_directory(simulation)
            exe = simulation_dir.joinpath(command)
            self.assertTrue(os.access(exe, os.X_OK))

    def testSingularity(self):
        command = "singularity exec /shared/rocky_dtk_runner_py39.sif Assets/hello.sh"
        task = CommandTask(command=command)
        task.common_assets.add_asset("input/hello.sh")

        # create experiment from task
        experiment = Experiment.from_task(task, name="run_task_in_singularity")
        suite = Suite(name='Idm Suite')
        suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
        # Add experiment to the suite
        suite.add_experiment(experiment)
        suite.run(platform=self.platform, wait_until_done=False, wait_on_done=False,
                  max_running_jobs=10,
                  retries=5, dry_run=True)
        for simulation in experiment.simulations:
            simulation_dir = self.platform._op_client.get_directory(simulation)
            exe = simulation_dir.joinpath("Assets/hello.sh")
            self.assertTrue(os.access(exe, os.X_OK))
