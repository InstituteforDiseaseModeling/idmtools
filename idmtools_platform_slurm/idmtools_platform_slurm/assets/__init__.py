from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from jinja2 import Template

from idmtools.entities.experiment import Experiment

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform, CONFIG_PARAMETERS

DEFAULT_TEMPLATE_FILE = Path(__file__).parent.joinpath("sbatch.sh.jinja2")


def generate_script(platform: 'SlurmPlatform', experiment: Experiment, max_running_jobs: Optional[int] = None, template: Union[Path,str] = DEFAULT_TEMPLATE_FILE, **kwargs):
    from idmtools_platform_slurm.slurm_platform import CONFIG_PARAMETERS
    template_vars = dict(njobs=experiment.simulation_count)
    # populate from our platform config vars
    for p in CONFIG_PARAMETERS:
        if getattr(platform, p) is not None:
            template_vars[p] = getattr(platform, p)

    # Set default here
    if max_running_jobs is None and platform.max_running_jobs is None:
        template_vars['max_running_jobs'] = 1

    # add any overides. We need some validation here later
    # TODO add validation for valid config options
    template_vars.update(**kwargs)

    if platform.modules:
        template_vars['modules'] = platform.modules

    with open(template) as file_:
        t = Template(file_.read())

    # Write our file
    output_target = platform._op_client.get_directory(experiment).joinpath("sbatch.sh")
    with open(output_target, "w") as tout:
        tout.write(t.render(**template_vars))
    # Make executable
    output_target.chmod(0o755)


def generate_simulation_script(platform: 'SlurmPlatform', sim_dir, simulation, retries: Optional[int] = None):
    sim_script = sim_dir.joinpath("_run.sh")
    with open(sim_script, "w") as tout:
        with open(Path(__file__).parent.parent.joinpath("assets/_run.sh.jinja2")) as tin:
            t = Template(tin.read())
            tvars = dict(
                platform=platform,
                simulation=simulation,
                retries=retries if retries else platform.retries
            )
            tout.write(t.render(*tvars))
    # TODO Add this command to ops
    sim_script.chmod(0o755)
