"""
Utility functions to generate batch scripts.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from jinja2 import Template
from typing import TYPE_CHECKING, Optional
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation

if TYPE_CHECKING:
    from idmtools_platform_file.file_platform import FilePlatform

DEFAULT_TEMPLATE_FILE = Path(__file__).parent.joinpath("batch.sh.jinja2")
DEFAULT_SIMULATION_TEMPLATE = Path(__file__).parent.parent.joinpath("assets/_run.sh.jinja2")


def generate_script(platform: 'FilePlatform', experiment: Experiment, max_job: int = None, run_sequence: bool = None,
                    **kwargs) -> None:
    """
    Generate batch file batch.sh.
    Args:
        platform: File Platform
        experiment: idmtools Experiment
        max_job: int
        run_sequence: bool
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    output_target = platform.get_directory(experiment).joinpath("batch.sh")
    with open(output_target, "w") as tout:
        with open(DEFAULT_TEMPLATE_FILE) as tin:
            t = Template(tin.read())
            tvars = dict(
                platform=platform,
                max_job=max_job if max_job is not None else platform.max_job,
                run_sequence=run_sequence if run_sequence is not None else platform.run_sequence
            )
            if platform.modules:
                tvars['modules'] = platform.modules
            if platform.extra_packages:
                tvars['packages'] = platform.extra_packages
            tout.write(t.render(tvars))

    # Make executable
    platform.update_script_mode(output_target)


def generate_simulation_script(platform: 'FilePlatform', simulation: Simulation, retries: Optional[int] = None,
                               **kwargs) -> None:
    """
    Generate batch file _run.sh.
    Args:
        platform: File Platform
        simulation: idmtools Simulation
        retries: int
        extra_packages: List of extra packages to install
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    sim_script = platform.get_directory(simulation).joinpath("_run.sh")
    with open(sim_script, "w") as tout:
        with open(DEFAULT_SIMULATION_TEMPLATE) as tin:
            t = Template(tin.read())
            tvars = dict(
                platform=platform,
                simulation=simulation,
                retries=retries if retries else platform.retries,
                mpi_procs = platform.mpi_procs
            )
            tout.write(t.render(tvars))

    # Make executable
    platform.update_script_mode(sim_script)
