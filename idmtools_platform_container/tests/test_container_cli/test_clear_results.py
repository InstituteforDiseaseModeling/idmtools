import os
import sys
import pytest
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_base import TestContainerPlatformCliBase


@pytest.mark.serial
class TestContainerPlatformClearResultsCli(TestContainerPlatformCliBase):

    def test_clear_results(self):
        command = "sleep 100"
        task = CommandTask(command=command)
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        result = self.runner.invoke(container_cli.container, ['clear-results', experiment.id])
        self.assertEqual(result.exit_code, 0)
        # check if the EXPERIMENT_FILES are removed
        for f in container_cli.EXPERIMENT_FILES:
            self.assertFalse(os.path.exists(os.path.join(self.job_directory, experiment.parent_id, experiment.id, f)))
        # check if the SIMULATION_FILES are removed
        for f in container_cli.SIMULATION_FILES:
            self.assertFalse(os.path.exists(
                os.path.join(self.job_directory, experiment.parent_id, experiment.id, experiment.simulations[0].id, f)))
        # clear-results Assets for simulation extra folder
        result = self.runner.invoke(container_cli.container, ['clear-results', experiment.id, '-r',
                                                              os.path.join(self.job_directory, experiment.parent_id,
                                                                           experiment.id, experiment.simulations[0].id,
                                                                           "Assets")])
        self.assertFalse(os.path.exists(
            os.path.join(self.job_directory, experiment.parent_id, experiment.id, experiment.simulations[0].id,
                         "Assets")))
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_clear_results_help(self):
        result = self.runner.invoke(container_cli.container, ['clear-results', "--help"])
        expected_help = ('Usage: container clear-results [OPTIONS] ITEM_ID\n'
                         '\n'
                         '  Clear job results files and folders.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    ITEM_ID: Experiment/Simulation ID\n'
                         '\n'
                         'Options:\n'
                         '  -r, --remove TEXT  Extra files/folders to be removed from simulation\n'
                         '  --help             Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)
