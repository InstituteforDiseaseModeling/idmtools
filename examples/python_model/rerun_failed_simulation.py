"""
This is the example of how to rerun failed simulations with an existing experiment.
Note, we can only rerun failed simulations due to server random failure.
"""
from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform

platform = Platform('Calculon')
# Get experiment by id
experiment = platform.get_item("fdc32be7-e960-f011-aa23-b88303911bc1", ItemType.EXPERIMENT)
# Get all failed simulations
filter_simulation_ids = experiment.get_simulations_by_tags(status=EntityStatus.FAILED)
print(filter_simulation_ids)

# rerun failed simulations. Note we can only rerun failed simulations due to server random failure.
failed_simulations = []
for sim_id in filter_simulation_ids:
    sim = platform.get_item(sim_id, ItemType.SIMULATION)
    # set the status to None so that we can rerun
    sim.status = None
    sim.tags.update({"rerun": sim.id})
    sim.assets.platform = None
    # TODO: modify failed simulation here:
    # reset task
    # cli=sim.task.command.cmd
    # sim.task =CommandTask(CommandLine.from_string(cli))
    failed_simulations.append(sim)
# Add failed simulations to the experiment
experiment.add_simulations(failed_simulations)
# run experiment again
experiment.run()





