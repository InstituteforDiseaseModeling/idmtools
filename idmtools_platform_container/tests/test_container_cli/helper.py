from unittest import mock
import idmtools_platform_container.cli.container as container_cli
from rich.table import Table


def get_jobs_from_cli(runner, container_id=None):
    """
    Get jobs from cli
    Args:
        runner:

    Returns:
        jobs table which containers row like [EXPERIMENT, experiment_id, job_id, container_id, status]
    """
    with mock.patch('rich.console.Console.print') as mock_console:
        if container_id:
            result = runner.invoke(container_cli.container, ['jobs', container_id])
        else:
            result = runner.invoke(container_cli.container, ['jobs'])
        actual_jobs_table = []
        for call in mock_console.call_args_list:
            args, _ = call

            for arg in args:
                if isinstance(arg, Table):
                    actual_rows = []
                    for c in arg.columns:
                        actual_rows.append(c._cells[0])
                    actual_jobs_table.append(actual_rows)
        return actual_jobs_table


def found_job_id_by_experiment(actual_jobs_table, experiment_id=None):
    """
    Find job id by experiment id
    Args:
        actual_jobs_table: the actual jobs table from 'idmtools container jobs' cli command
        experiment_id:

    Returns:
        job_id, container_id
    """
    for row in actual_jobs_table:
        if row[1] == experiment_id:
            return row[2], row[3]
    return None
