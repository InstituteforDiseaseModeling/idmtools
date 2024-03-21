###################################
# This example provides how you can check if your sweeps are working as expected
###################################
from functools import partial
from idmtools.builders import ArmSimulationBuilder, SweepArm, ArmType
from idmtools.entities.command_task import CommandTask
from idmtools.entities.templated_simulation import TemplatedSimulations
from tabulate import tabulate


def update_parameter(simulation, parameter, value):
    simulation.task.config[parameter] = value


base_task = CommandTask('example')
base_task.config = dict(enable_births=False)
builder = ArmSimulationBuilder()
# Define our first set of sweeps
arm = SweepArm(type=ArmType.cross)
arm.add_sweep_definition(partial(update_parameter, parameter='population'), [500, 1000])
arm.add_sweep_definition(partial(update_parameter, parameter='susceptible'), [0.5, 0.9])
builder.add_arm(arm)
# Now add the sweeps with the birth_rate as well
arm2 = SweepArm(type=ArmType.cross)
arm2.add_sweep_definition(partial(update_parameter, parameter='enable_births'), [True])
arm2.add_sweep_definition(partial(update_parameter, parameter='birth_rate'), [0.01, 0.1])
builder.add_arm(arm2)

sims = TemplatedSimulations(base_task=base_task)
sims.add_builder(builder)

print(tabulate([s.task.config for s in sims], headers="keys"))
