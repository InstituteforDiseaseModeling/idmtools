import os
import sys
from functools import partial

from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.simulation import Simulation

command_format_str = "singularity exec ./Assets/covasim_ubuntu.sif python3 Assets/run_sim1.py {pop_size} {pop_infected} {n_days} {rand_seed}"

def create_config_before_provisioning(simulation: Simulation, platform: IPlatform):
    # set the command dynamically
    simulation.task.command = CommandLine.from_string(command_format_str.format(**simulation.task.config))


def set_value(simulation, name, value):
    simulation.task.config[name] = round(value, 2) if isinstance(value, float) else value
    # add tag with our value
    simulation.tags[name] = round(value, 2) if isinstance(value, float) else value

if __name__ == "__main__":
    here = os.path.dirname(__file__)

    # Create a platform to run the workitem
    platform = Platform("CALCULON")

    # create commandline input for the task
    command = CommandLine("singularity exec ./Assets/covasim_ubuntu.sif python3 Assets/run_sim_sweep.py")
    task = CommandTask(command=command)

    task.config = dict(pop_size=1000, pop_infected=10, n_days=120, rand_seed=1)
    task.add_pre_creation_hook(create_config_before_provisioning)

    # Add our image
    task.common_assets.add_assets(AssetCollection.from_id_file("covasim.id"))

    sb = SimulationBuilder()
    # Add sweeps on 3 parameters. Total of 1680 simulations(6x14x21)
    sb.add_sweep_definition(partial(set_value, name="pop_size"), [10000, 20000])
    sb.add_sweep_definition(partial(set_value, name="pop_infected"), [10, 100, 1000])
    sb.add_sweep_definition(partial(set_value, name="n_days"), [100, 110, 120])
    sb.add_sweep_definition(partial(set_value, name="rand_seed"), [1234, 4567])


    experiment = Experiment.from_builder(sb, base_task=task, name=os.path.split(sys.argv[0])[1])
    experiment.add_asset(os.path.join("inputs", "run_sim_sweep.py"))
    experiment.add_asset(os.path.join("inputs", "sim_to_inset.py"))
    experiment.run(wait_until_done=True)
    if experiment.succeeded:
        experiment.to_id_file("run_sim_sweep.id")
