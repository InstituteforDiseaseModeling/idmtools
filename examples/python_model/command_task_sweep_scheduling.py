import os
import sys
from functools import partial
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_comps.utils.scheduling import default_add_workerorder_sweep_callback


# Update each sweep parameter in simulation and add to command line argument to command
def set_value(simulation, name, value):
    fix_value = round(value, 2) if isinstance(value, float) else value
    # add argument
    simulation.task.command.add_raw_argument(str(fix_value))
    # add tag with our value
    simulation.tags[name] = fix_value


# create command line
command = CommandLine("python3 Assets/commandline_model.py")
# create CommandTask
task = CommandTask(command=command)
ts = TemplatedSimulations(base_task=task)

sb = SimulationBuilder()
sb.add_sweep_definition(partial(set_value, name="pop_size"), [10000, 20000])
sb.add_sweep_definition(partial(set_value, name="pop_infected"), [10, 100])
sb.add_sweep_definition(partial(set_value, name="n_days"), [100, 110])
sb.add_sweep_definition(partial(set_value, name="rand_seed"), [1234, 4567])
sb.add_sweep_definition(partial(default_add_workerorder_sweep_callback, file_name="WorkOrder.json"),
                        file_path=os.path.join("inputs", "scheduling", "WorkOrder_orig.json"))

ts.add_builder(sb)

experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
experiment.add_asset(os.path.join("inputs", "scheduling", "commandline_model.py"))

with Platform('CALCULON') as platform:
    experiment.run(wait_on_done=True, scheduling=True)
    # use system status as the exit code
    sys.exit(0 if experiment.succeeded else -1)
