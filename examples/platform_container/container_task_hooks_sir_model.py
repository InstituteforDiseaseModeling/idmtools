# This script is an example of how to use ContainerPlatform to run simulations with Commandtask task that has hooks
# to set the command and tags for each simulation.
import copy
from functools import partial
from logging import getLogger
import numpy
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.simulation import Simulation
from idmtools_platform_container.container_platform import ContainerPlatform

command_format_str = "python3 Assets/sir.py --N {n} --I0 {i0} --R0 {r0} --gamma {gamma} --beta {beta}"
user_logger = getLogger('user')


# create_task_command_hook function will get called by idmtoola internally which is before the simulation is created,
# and it will set the command for each simulation based on the parameters which are set in the task including the sweep values.
def create_task_command_hook(simulation: Simulation, platform: IPlatform):
    # set the command dynamically.
    # or example, command string will be like "python3 Assets/sir.py --N 1000 --I0 1 --R0 0 --gamma 0.1 --beta 0.01"
    # all the specific values are set in the simulation.task.params
    simulation.task.command = CommandLine.from_string(command_format_str.format(**simulation.task.params))
    user_logger.info(f"Set command for simulation to: {simulation.task.command}")
    # return configs as tags
    return copy.deepcopy(simulation.task.params)


# set_value function will be called by idmtools internally before above create_task_command_hook function get called.
# It will set the value of the parameter in the simulation task by sweeping function.
def set_parameter(simulation, name, value):
    simulation.task.params[name] = value
    # add tag with our value
    simulation.tags[name] = value
    return {name: value}


platform = ContainerPlatform(job_directory="DEST")
# add the python sir.py script as a common asset
ac = AssetCollection()
ac.add_asset("inputs/sir_model/sir.py")

# create CommandTask task with the command to run the sir.py script
task = CommandTask(command="python3 Assets/sir.py", common_assets=ac)
# set base parameters for the sir.py script
task.params = dict(n=1000, i0=1, r0=0, beta=0.2, gamma=1./10)
# add the hook to set the command for each simulation
task.add_pre_creation_hook(create_task_command_hook)

sb = SimulationBuilder()
# Add sweeps on 3 parameters. Total of 6*14*20 = 1680 simulations
sb.add_sweep_definition(partial(set_parameter, name="i0"), range(20, 260, 40))   # 6
sb.add_sweep_definition(partial(set_parameter, name="gamma"), numpy.arange(0.1, 0.8, 0.05))  # 14
sb.add_sweep_definition(partial(set_parameter, name="beta"), numpy.arange(0.01, 1, 0.05))  # 20

experiment = Experiment.from_builder(sb, base_task=task, name="container_with_sweeping_task")
experiment.run(wait_until_done=True, platform=platform)
