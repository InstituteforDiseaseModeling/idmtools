"""
This is the example of how to rerun failed simulations with an existing experiment.
Note, we can only rerun failed simulations due to server random failure.
"""
from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask

platform = Platform('Calculon')
# Get experiment by id
experiment = platform.get_item("fdc32be7-e960-f011-aa23-b88303911bc1", ItemType.EXPERIMENT)
# Get all failed simulations
filter_simulation_ids = experiment.get_simulations_by_tags(status=EntityStatus.FAILED)
print(filter_simulation_ids)

# Let's get first failed simulation, and modify it
sim = platform.get_item(filter_simulation_ids[0], ItemType.SIMULATION)
# set the status to None so that we can rerun
sim.status = None
sim.tags.update({"rerun": sim.id})
sim.assets.platform = None
# TODO: modify failed simulation here:
# For this example we change command to make previous failed sim pass. But in real case, you need to fix your model
sim.task =CommandTask("python3 --version")
# Add failed simulation to the experiment
experiment.add_simulation(sim)
# run experiment again
experiment.run()





