import re

from rich.table import Table


def get_actual_rich_table_values(mock_console):
    """
    Get actual table values from the mock console
    Args:
        mock_console: rich.console.Console

    Returns:
        list for actual table values
    """
    actual_table = []
    head = []
    for call in mock_console.call_args_list:
        args, _ = call

        for arg in args:
            if isinstance(arg, Table):
                actual_rows = []
                if len(head) == 0:
                    head = [column.header for column in arg.columns]
                    actual_table.append(head)
                for c in arg.columns:
                    actual_rows.append(c._cells[0])
                actual_table.append(actual_rows)
    return actual_table


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


def cleaned_str(input_string):
    """
    Remove all substrings enclosed in brackets, leading spaces, and newlines
    Args:
        input_string: str

    Returns:
        cleaned string
    """
    return re.sub(r'^\s+|\[.*?\]|\n', '', input_string)