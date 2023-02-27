from pathlib import Path
from jinja2 import Template
from typing import TYPE_CHECKING, Optional, Union
from idmtools.entities.experiment import Experiment

if TYPE_CHECKING:
    from idmtools_platform_file.file_platform import FilePlatform

DEFAULT_TEMPLATE_FILE = Path(__file__).parent.joinpath("batch.sh.jinja2")
DEFAULT_SIMULATION_TEMPLATE = Path(__file__).parent.parent.joinpath("assets/_run.sh.jinja2")


def generate_script(platform: 'FilePlatform', experiment: Experiment,
                    template: Union[Path, str] = DEFAULT_TEMPLATE_FILE, **kwargs) -> None:
    """
    Generate batch file batch.sh.
    Args:
        platform: File Platform
        experiment: idmtools Experiment
        template: template to be used to build batch file
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    template_vars = dict()

    # with open(template) as file_:     # TODO: take input template
    with open(DEFAULT_TEMPLATE_FILE) as file_:
        t = Template(file_.read())

    # Write our file
    output_target = platform.get_directory(experiment).joinpath("batch.sh")
    with open(output_target, "w") as tout:
        tout.write(t.render(template_vars))


def generate_simulation_script(platform: 'FilePlatform', simulation, retries: Optional[int] = None,
                               template: str = DEFAULT_SIMULATION_TEMPLATE) -> None:
    """
    Generate batch file _run.sh.
    Args:
        platform: File Platform
        simulation: idmtools Simulation
        retries: int
        template: user template
    Returns:
        None
    """
    sim_script = platform.get_directory(simulation).joinpath("_run.sh")
    with open(sim_script, "w") as tout:
        # with open(template) as tin:         # TODO: take input template
        with open(DEFAULT_SIMULATION_TEMPLATE) as tin:
            t = Template(tin.read())
            tvars = dict(
                platform=platform,
                simulation=simulation,
                retries=retries if retries else platform.retries
            )
            tout.write(t.render(tvars))
