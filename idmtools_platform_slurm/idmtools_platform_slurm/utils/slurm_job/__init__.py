"""
idmtools SlurmPlatform SlurmJob utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

INDICATOR_VARIABLE = 'RUN_ON_SLURM'


def create_slurm_indicator() -> NoReturn:
    """
    Add environment variable.
    Returns:
        None
    """
    os.environ[INDICATOR_VARIABLE] = '1'


def remove_slurm_indicator() -> NoReturn:
    """
    Remove the environment variable.
    Returns:
        None
    """
    os.environ.pop(INDICATOR_VARIABLE, None)


def check_slurm_indicator() -> bool:
    """
    Check if the environment set to '1'.
    Returns:
        True/False
    """
    return os.environ.get(INDICATOR_VARIABLE, '0') == '1'


def slurm_installed() -> bool:
    """
    Check if Slurm system is installed or available.
    Returns:
        True/False
    """
    try:
        subprocess.check_output(["sinfo", "-V"])
        return True
    except:
        return False


def run_script_on_slurm(platform: 'SlurmPlatform', run_on_slurm: bool = False,
                        cleanup: bool = True) -> bool:
    """
    This is a utility tool which wraps the SlurmJob creation and run.
    Args:
        platform: idmtools Platform
        run_on_slurm: True/False
        cleanup: True/False to delete the generated slurm job related files
    Returns:
        True/False
    """
    from idmtools_platform_slurm.utils.slurm_job.slurm_job import SlurmJob
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

    # Double make sure it is Slurm Platform
    if not isinstance(platform, SlurmPlatform):
        return False

    if run_on_slurm and not check_slurm_indicator():
        # Locate the script
        # Wrong path due to emod_malaria bug:
        # script = os.path.abspath(sys.argv[0])
        # Workaround: manually build full path
        script = Path(sys.path[0]).joinpath(Path(sys.argv[0]).name)
        # Collect script input parameters
        script_params = sys.argv[1:]
        # Run script as Slurm job
        sj = SlurmJob(script_path=script, platform=platform, script_params=script_params, cleanup=cleanup)
        # Kick off Slurm job
        sj.run()
        return True
    else:
        return False
