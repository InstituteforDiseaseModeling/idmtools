from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.comps_platform import COMPSPlatform
from idmtools_test.utils.itest_with_persistence import ITestWithPersistence


class TestIPlatform(ITestWithPersistence):

    def test_comp_platform_bug_2327(self):
        platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="SlurmStage")
        command = "python3 --version"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="bug_2327")
        # This bug used to fail with no platform argument in run method. Should be fixed now
        experiment.run(wait_until_done=True)