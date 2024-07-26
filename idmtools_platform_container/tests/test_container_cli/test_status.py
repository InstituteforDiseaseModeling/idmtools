import os
import sys
import unittest
from unittest import mock
import pytest
from idmtools.builders import SimulationBuilder
from idmtools.core import ItemType
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
import idmtools_platform_container.cli.container as container_cli
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_container.container_platform import ContainerPlatform
from idmtools_platform_container.utils.general import normalize_path

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)
from test_base import TestContainerPlatformCliBase
from helper import get_actual_rich_table_values, found_job_id_by_experiment, cleaned_str


@pytest.mark.serial
class TestContainerPlatformStatusCli(TestContainerPlatformCliBase):
    def test_status(self):
        command = "python3 Assets/sleep.py"
        task = CommandTask(command=command)
        task.common_assets.add_asset(os.path.join(script_dir, "..", "inputs", "sleep.py"))
        experiment = Experiment.from_task(task, name="run_command")
        experiment.run(wait_until_done=False)
        exp_dir = self.platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)

        # test status with experiment id
        with mock.patch('rich.console.Console.print') as mock_console:
            result = self.runner.invoke(container_cli.container, ['status', experiment.id])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(normalize_path(exp_dir), mock_console.call_args_list[0].args[0])
            self.assertIn('Simulation Count', cleaned_str(mock_console.call_args_list[1][0][0]))
            self.assertIn('SUCCEEDED', cleaned_str(mock_console.call_args_list[2][0][0]))
            self.assertIn('FAILED', cleaned_str(mock_console.call_args_list[3][0][0]))
            self.assertIn('RUNNING', cleaned_str(mock_console.call_args_list[4][0][0]))
            self.assertIn('PENDING', cleaned_str(mock_console.call_args_list[5][0][0]))

        # test status with experiment id and container id
        with mock.patch('rich.console.Console.print') as mock_console_container:
            result = self.runner.invoke(container_cli.container,
                                        ['status', experiment.id, '-c', self.platform.container_id])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(normalize_path(exp_dir), mock_console_container.call_args_list[0].args[0])
            self.assertIn('Simulation Count', cleaned_str(mock_console_container.call_args_list[1][0][0]))
            self.assertIn('SUCCEEDED', cleaned_str(mock_console_container.call_args_list[2][0][0]))
            self.assertIn('FAILED', cleaned_str(mock_console_container.call_args_list[3][0][0]))
            self.assertIn('RUNNING', cleaned_str(mock_console_container.call_args_list[4][0][0]))
            self.assertIn('PENDING', cleaned_str(mock_console_container.call_args_list[5][0][0]))

        # test status with simulation id
        with mock.patch('rich.console.Console.print') as mock_console_sim:
            print("simulations", experiment.simulations[0].id)
            result = self.runner.invoke(container_cli.container, ['status', experiment.simulations[0].id])
            self.assertEqual(result.exit_code, 0)
            self.assertIn(f'SIMULATION {experiment.simulations[0].id} is ',
                          mock_console_sim.call_args_list[0][0][0])

        # test status with wrong id
        with mock.patch('idmtools_platform_container.cli.container.user_logger') as user_logger:
            result = self.runner.invoke(container_cli.container, ['status', "sim_id"])
            self.assertEqual(result.exit_code, 0)
            user_logger.warning.assert_called_with("Job sim_id not found.")

        # test status with job id
        with mock.patch('rich.console.Console.print') as mock_console_jobs:
            # first find job id:
            result = self.runner.invoke(container_cli.container, ['jobs'])
            self.assertEqual(result.exit_code, 0)
            actual_table = get_actual_rich_table_values(mock_console_jobs)
            job_id, container_id = found_job_id_by_experiment(actual_table, experiment.id)
            # test status with job id
            with mock.patch('rich.console.Console.print') as mock_console_job:
                result = self.runner.invoke(container_cli.container, ['status', job_id])
                self.assertEqual(result.exit_code, 0)
                self.assertIn(normalize_path(exp_dir), mock_console_job.call_args_list[0].args[0])
                self.assertIn('Simulation Count', cleaned_str(mock_console_job.call_args_list[1][0][0]))
                self.assertIn('SUCCEEDED', cleaned_str(mock_console_job.call_args_list[2][0][0]))
                self.assertIn('FAILED', cleaned_str(mock_console_job.call_args_list[3][0][0]))
                self.assertIn('RUNNING', cleaned_str(mock_console_job.call_args_list[4][0][0]))
                self.assertIn('PENDING', cleaned_str(mock_console_job.call_args_list[5][0][0]))

        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', self.platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    # test status with verbose and limit. For this test, we generate 9 simulations, but only show 2 in the output
    @mock.patch('rich.console.Console.print')
    def test_status_with_verbose_and_limit(self, mock_console):
        platform = ContainerPlatform(job_directory=self.job_directory, new_container=True)
        command = "python3 Assets/sleep.py"
        task = CommandTask(command=command)
        task.common_assets.add_asset(os.path.join(script_dir, "..", "inputs", "sleep.py"))
        ts = TemplatedSimulations(base_task=task)
        sb = SimulationBuilder()

        def update_parameter_callback(simulation, sleep_time):
            simulation.task.command.add_argument(sleep_time)
            return {'sleep_time': sleep_time}

        sb.add_sweep_definition(update_parameter_callback, sleep_time=range(1, 10))
        ts.add_builder(sb)
        experiment = Experiment.from_template(ts, name="run_sweep_sleep")
        experiment.run(wait_until_done=True, platform=platform)
        exp_dir = platform.get_directory_by_id(experiment.id, ItemType.EXPERIMENT)
        # we only show 2 simulation details in the output
        result = self.runner.invoke(container_cli.container,
                                    ['status', experiment.id, '-l', 2, '--verbose'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn(normalize_path(exp_dir), mock_console.call_args_list[0].args[0])
        self.assertEqual('Simulation Count: 9', cleaned_str(mock_console.call_args_list[1][0][0]))
        self.assertEqual('SUCCEEDED (9)', cleaned_str(mock_console.call_args_list[2][0][0]))
        self.assertEqual('...', cleaned_str(mock_console.call_args_list[5][0][0]))
        self.assertEqual('FAILED (0)', cleaned_str(mock_console.call_args_list[6][0][0]))
        self.assertIn('RUNNING', cleaned_str(mock_console.call_args_list[7][0][0]))
        self.assertIn('PENDING', cleaned_str(mock_console.call_args_list[8][0][0]))
        # verify there are 2 lines with simulations
        simulation_ids = [simulation.id for simulation in experiment.simulations]
        self.assertTrue(cleaned_str(mock_console.call_args_list[3][0][0]) in simulation_ids)
        self.assertTrue(cleaned_str(mock_console.call_args_list[4][0][0]) in simulation_ids)
        # clean up container
        result = self.runner.invoke(container_cli.container, ['stop-container', platform.container_id], '--remove')
        self.assertEqual(result.exit_code, 0)

    def test_status_help(self):
        result = self.runner.invoke(container_cli.container, ['status', "--help"])
        expected_help = ('Usage: container status [OPTIONS] ITEM_ID\n'
                         '\n'
                         '  Check the status of an Experiment/Simulation.\n'
                         '\n'
                         '  Arguments:\n'
                         '\n'
                         '    ITEM_ID: Experiment/Simulation ID or Job ID\n'
                         '\n'
                         'Options:\n'
                         '  -c, --container_id TEXT   Container Id\n'
                         '  -l, --limit INTEGER       Max number of simulations to show\n'
                         '  --verbose / --no-verbose  Display with working directory or not\n'
                         '  --help                    Show this message and exit.\n')
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_help)


if __name__ == '__main__':
    unittest.main()
