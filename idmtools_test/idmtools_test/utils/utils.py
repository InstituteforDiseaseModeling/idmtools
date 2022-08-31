import sys
from io import StringIO
from contextlib import contextmanager
import os
import shutil
import subprocess
import pandas as pd
from idmtools.entities.simulation import Simulation


def get_case_name(name: str):
    """
    Add prefix from environment var to names of experiments
    Args:
        name:

    Returns:

    """
    if os.environ.get("IDMTOOLS_TEST_PREFIX", None):
        return f'{os.environ["IDMTOOLS_TEST_PREFIX"]}.{name}'
    return name


def del_folder(path: str):
    """
    Delete Folder

    Args:
        path: Path to delete

    Returns:

    """
    if os.path.exists(path):
        shutil.rmtree(path)


def del_file(filename: str, dir: str = None):
    """
    Delete a file

    Args:
        filename: Filename
        dir: Optional Directory

    Returns:

    """
    if dir:
        filepath = os.path.join(dir, filename)
    else:
        filepath = os.path.join(os.path.curdir, filename)

    if os.path.exists(filepath):
        print(filepath)
        os.remove(filepath)


def load_csv_file(filename: str, dir: str = None) -> pd.DataFrame():
    """
    Load CSV File

    Args:
        filename: Filename
        dir: Optional Directory

    Returns:

    """
    df = None
    if dir:
        filepath = os.path.join(dir, filename)
    else:
        filepath = os.path.join(os.path.curdir, filename)

    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    return df


def verify_simulation(simulation: Simulation, expected_parameters, expected_values):
    for value_set in expected_values:
        for i, value in enumerate(list(value_set)):
            if not simulation.task.parameters[expected_parameters[i]] == expected_values:
                break
        return True
    return False


def load_python_files_from_folder(analyzers_folder):
    for file in os.listdir(analyzers_folder):
        if '.py' in file:
            yield file


def execute_example(cmd, cwd=None, shell=True):
    popen_opts = dict(shell=shell)
    if cwd:
        popen_opts['cwd'] = cwd
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                             **popen_opts)
    for stdout_line in iter(popen.stdout.readline, ""):
        print(stdout_line.strip())
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
    return return_code


def test_example_folder(tc, analyzers_folder):
    for file in load_python_files_from_folder(analyzers_folder):
        with tc.subTest(file):
            working_directory = analyzers_folder
            try:
                print(f'Running example: python {file}')
                result = execute_example(f'python {file}', cwd=working_directory, shell=True)
                tc.assertEqual(result, 0)
            except subprocess.CalledProcessError as e:
                tc.assertEqual(result, e.returncode, f'Result for example {file} failed. See {e.output}')


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def is_global_configuration_enabled() -> bool:
    from idmtools import IdmConfigParser
    return os.path.exists(IdmConfigParser.get_global_configuration_name()) or os.environ.get("IDMTOOLS_CONFIG_FILE", None) is not None


def get_performance_scale() -> int:
    try:
        scale = int(os.getenv("IDMTOOLS_TEST_SCALE", "1"))
    except:
        scale = 1
    return scale


def clear_id_cache():
    from idmtools.core.interfaces.iitem import get_id_generator
    from idmtools.plugins.item_sequence import get_plugin_config
    get_id_generator.cache_clear()
    get_plugin_config.cache_clear()
