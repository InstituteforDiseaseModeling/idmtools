import json
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture
def slurm_bridge_test_dir() -> str:
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)


@pytest.fixture
def slurm_bridge_command_sbatch_valid(slurm_bridge_test_dir: str) -> str:
    """
    This fixture creates a sbatch request that is valid, but has no backing files.

    Args:
        slurm_bridge_test_dir: Directory to use for testing

    Returns:
        Job file path
    """
    job_name = Path(slurm_bridge_test_dir).joinpath(str(uuid4())).joinpath("job.json")
    job_name.parent.mkdir(parents=True, exist_ok=True)
    with open(job_name, 'w') as job_out:
        json.dump(dict(
            command='sbatch',
            working_directory=str(job_name.parent)
        ), job_out)
    yield str(job_name)


@pytest.fixture
def slurm_bridge_command_sbatch_invalid(slurm_bridge_test_dir: str) -> str:
    """
    This fixture creates a sbatch request that is valid, but has no backing files.

    Args:
        slurm_bridge_test_dir: Directory to use for testing

    Returns:
        Job file path
    """
    job_name = Path(slurm_bridge_test_dir).joinpath(str(uuid4())).joinpath("job.json")
    job_name.parent.mkdir(parents=True, exist_ok=True)
    with open(job_name, 'w') as job_out:
        json.dump(dict(
            command='sbatch',
        ), job_out)
    yield str(job_name)


@pytest.fixture
def slurm_bridge_command_invalid(slurm_bridge_test_dir):
    job_name = Path(slurm_bridge_test_dir).joinpath(str(uuid4())).joinpath("job.json")
    job_name.parent.mkdir(parents=True, exist_ok=True)
    with open(job_name, 'w') as job_out:
        json.dump(dict(
            command='Invalid command'
        ), job_out)
    yield str(job_name)
