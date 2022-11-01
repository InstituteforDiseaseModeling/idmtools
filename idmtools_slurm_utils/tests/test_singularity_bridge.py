from os import PathLike
from unittest import mock

import pytest_mock

import idmtools_slurm_utils
from idmtools_slurm_utils.sbatch import ERROR_NO_WORKING_DIRECTORY
from idmtools_slurm_utils.utils import get_job_result, ERROR_INVALID_COMMAND


def test_command_job(slurm_bridge_command_sbatch_valid: PathLike, mocker: pytest_mock.MockerFixture):
    # Patch our call so we don't need to call actual slurm here
    mocker.patch('idmtools_slurm_utils.sbatch.run_sbatch', return_value=
    ('Example Output', 0))
    result = get_job_result(slurm_bridge_command_sbatch_valid)
    idmtools_slurm_utils.sbatch.run_sbatch.assert_called_once()
    assert 'output' in result
    assert 'return_code' in result
    assert 'status' in result
    assert result['status'] == 'success'
    assert result['return_code'] == 0
    assert result['output'] == "Example Output"


def test_command_job_invalid(slurm_bridge_command_sbatch_invalid: PathLike):
    # Patch our call so we don't need to call actual slurm here

    result = get_job_result(slurm_bridge_command_sbatch_invalid)
    assert 'output' in result
    assert 'return_code' in result
    assert 'status' in result
    assert result['status'] == 'error'
    assert result['return_code'] == -1
    assert result['output'] == ERROR_NO_WORKING_DIRECTORY


def test_command_invalid(slurm_bridge_command_invalid: PathLike):
    result = get_job_result(slurm_bridge_command_invalid)
    assert 'output' in result
    assert 'status' in result
    assert result['status'] == 'error'
    assert result['output'] == ERROR_INVALID_COMMAND
