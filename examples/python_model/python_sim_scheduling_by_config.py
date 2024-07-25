# This example demonstrates how to use the default_add_schedule_config_sweep_callback which calls add_schedule_config to
# add workorder.json to each simulation with sweeping cmd arguments
import os
import sys
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_comps.utils.scheduling import default_add_schedule_config_sweep_callback

def update_parameter_callback(simulation, pop_size, pop_infected, n_days, rand_seed):
    simulation.task.command.add_argument(pop_size)
    simulation.task.command.add_argument(pop_infected)
    simulation.task.command.add_argument(n_days)
    simulation.task.command.add_argument(rand_seed)
    return {"pop_size": pop_size, "pop_infected": pop_infected, "n_days": n_days, "rand_seed": rand_seed}


# create command line
command = CommandLine("python3 Assets/commandline_model.py")
# create CommandTask
task = CommandTask(command=command)
ts = TemplatedSimulations(base_task=task)

sb = SimulationBuilder()
sb.add_sweep_definition(update_parameter_callback, pop_size=[10000, 20000], pop_infected=[10, 100],
                                           n_days=[100, 110], rand_seed=[1234, 4567])

# using default_add_schedule_config_sweep_callback to add workorder.json to each simulation with updated cmd arguments
sb.add_sweep_definition(
    partial(default_add_schedule_config_sweep_callback,
            command="python3 Assets/commandline_model.py {pop_size} {pop_infected} {n_days} {rand_seed}"),
    [dict(NodeGroupName='idm_cd', NumProcesses=1, NumNodes=2, Environment={"key1": "value1", "key2": "value2"})])
ts.add_builder(sb)

experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
experiment.add_asset(os.path.join("inputs", "scheduling", "commandline_model.py"))
with Platform('CALCULON') as platform:
    experiment.run(wait_until_done=True, scheduling=True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
