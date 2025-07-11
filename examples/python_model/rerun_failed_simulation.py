"""
This is the example of how to get failed simulation and rerun them with an existing experiment
"""
import copy

from idmtools.core import ItemType, EntityStatus
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask

platform = Platform('Calculo')
# Get experiment by id
experiment = platform.get_item("90ba4f1e-c45d-f011-aa23-b88303911bc1", ItemType.EXPERIMENT)
# Get all failed simulations
filter_simulation_ids = experiment.get_simulations_by_tags(status=EntityStatus.FAILED)
print(filter_simulation_ids)

# rerun failed simulations, and deepcopy each simulation to avoid changing the original simulation
failed_simulations = []
for sim_id in filter_simulation_ids:
    sim = platform.get_item(filter_simulation_ids[0], ItemType.SIMULATION)
    # set status to None so that we can rerun
    sim.status = None
    sim.tags.update({"rerun": "true"})
    # TODO: modify failed simulation here:
    # reset task
    # cli=sim.task.command.cmd
    # sim.task =CommandTask(CommandLine.from_string(cli))
    failed_simulations.append(copy.deepcopy(sim))
# Add failed simulations to the experiment
experiment.simulations.extend(failed_simulations)
# run experiment again
experiment.run(wait_until_done=True)





