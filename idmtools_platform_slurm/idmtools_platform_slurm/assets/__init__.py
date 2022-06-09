from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from jinja2 import Template

from idmtools.entities.experiment import Experiment

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

DEFAULT_TEMPLATE_FILE = Path(__file__).parent.joinpath("sbatch.sh.jinja2")

def generate_script(platform: SlurmPlatform, experiment: Experiment, max_running_jobs: Optional[int] = None, template: Union[Path,str] = DEFAULT_TEMPLATE_FILE, **kwargs):
    template_vars = dict(njobs=experiment.simulation_count)
    if max_running_jobs is not None:
        template_vars['max_running_jobs'] = max_running_jobs
    # populate from our platform config vars
    for p in ['ntasks', 'partition', 'nodes', 'mail_type', 'mail_user', 'ntasks_per_core', 'mem_per_cpu', 'time', 'account', 'mem', 'exclusive', 'requeue', 'sbatch_custom']:
        if getattr(platform, p) is not None:
            template_vars[p] = getattr(platform, p)

    # add any ovverides. We need some validation here later
    # TODO add validation for valid config options
    template_vars.update(**kwargs)

    if platform.modules:
        template_vars['modules'] = platform.modules

    with open(DEFAULT_TEMPLATE_FILE) as file_:
        t = Template(file_.read())

    output_target = "abc"
    with open(output_target, "w") as tout:
        tout.write(t.render(**template_vars))
