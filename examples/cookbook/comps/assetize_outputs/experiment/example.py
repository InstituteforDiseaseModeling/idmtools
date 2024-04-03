from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.utils.assetize_output.assetize_output import AssetizeOutput


############## Setup outputs to assetize in demo

base_task = CommandTask(command="python3 model.py")
base_task.common_assets.add_asset("model.py")
# Command task have no configs. Since it is a python object, we add our own item
base_task.config = dict(a=1,b=1)

# define a template for our commands
command_template = "python Assets/model.py --a {a} --b {b}"


# Define a function that renders our command line as we build simulations
def create_command_line_hook(simulation, platform):
    # we get our simulations object. Use the task and render our command line
    simulation.task.command = command_template.format(**simulation.task.config)


# Define sweeps
def set_parameter(simulation, parameter, value):
    simulation.task.config[parameter] = value


# add hook to our base task
base_task.add_pre_creation_hook(create_command_line_hook)
builder = SimulationBuilder()
builder.add_sweep_definition(partial(set_parameter, parameter="a"), range(3))
builder.add_sweep_definition(partial(set_parameter, parameter="b"), range(3))

platform = Platform("CALCULON")

experiment = Experiment.from_builder(builders=builder, base_task=base_task, name="Create example output")

############### Demo of assetize of experiment outputs
# Define what we want to assetize output
ao = AssetizeOutput(file_patterns=["output.json"], related_experiments=[experiment])
# run the Assetize job. It will ensure other items are ran if they are entities(Experiment, Simulation or Workitems)
ao.run(wait_until_done=True)
print(f"Asset Collection: {ao.id}")
