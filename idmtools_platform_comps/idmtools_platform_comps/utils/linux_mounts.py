"""idmtools set linux mounts.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from COMPS import AuthManager
from COMPS.Data import Simulation
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

DEFAULT_ENVIRONMENTS = ["SLURMSTAGE", "CALCULON"]


def set_linux_mounts(platform: 'IPlatform', linux_environment: str = None) -> None:
    """
    For COMPS Platform, check and set linux mounts.
    Args:
        platform: idmtools COMPS Platform
        linux_environment: platform environment

    Returns:
        None
    """
    linux_envs = DEFAULT_ENVIRONMENTS
    if linux_environment is not None:
        linux_envs.append(linux_environment.upper())

    if platform.environment.upper() in linux_envs:
        mounts = AuthManager.get_environment_macros(platform.environment)['DOCKER_MOUNTS']
        mounts = {v[0]: v[1:4] for v in [m.split(';') for m in mounts.split('|')]}
        # pretend I'm on Linux and set the Linux mapping environment variables
        for k, v in mounts.items():
            os.environ[k] = ';'.join([v[0], v[2]])


def clear_linux_mounts(platform: 'IPlatform', linux_environment: str = None) -> None:
    """
    For COMPS Platform, check and clear linux mounts.
    Args:
        platform: idmtools COMPS Platform
        linux_environment: platform environment

    Returns:
        None
    """
    linux_envs = DEFAULT_ENVIRONMENTS
    if linux_environment is not None:
        linux_envs.append(linux_environment.upper())

    if platform.environment.upper() in linux_envs:
        mounts = AuthManager.get_environment_macros(platform.environment)['DOCKER_MOUNTS']
        mounts = {v[0]: v[1:4] for v in [m.split(';') for m in mounts.split('|')]}
        # pretend I'm on Linux and clear the Linux mapping environment variables
        for k, v in mounts.items():
            os.environ.pop(k)


def get_workdir_from_simulations(platform: 'IPlatform', comps_simulations: List[Simulation]) -> Dict[str, str]:
    """
    Get COMPS simulations working directory.
    Args:
        platform: idmtools COMPS Platform
        comps_simulations: COMPS Simulations

    Returns:
        dictionary with simulation id as key and working directory as value
    """
    set_linux_mounts(platform)
    sim_work_dir = {str(sim.id): sim.hpc_jobs[-1].working_directory for sim in comps_simulations if sim.hpc_jobs}
    clear_linux_mounts(platform)
    return sim_work_dir
