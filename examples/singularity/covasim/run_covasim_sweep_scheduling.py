import os
import sys
from functools import partial
from idmtools.assets import AssetCollection
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_comps.utils.scheduling import default_add_workerorder_sweep_callback


def set_value(simulation, name, value):
    fix_value = round(value, 2) if isinstance(value, float) else value
    # add argument
    simulation.task.command.add_raw_argument(str(fix_value))
    # add tag with our value
    simulation.tags[name] = fix_value


if __name__ == "__main__":
    here = os.path.dirname(__file__)
    # Create a platform to run the workitem
    platform = Platform("CALCULON")
    # create commandline input for the task
    command = CommandLine(f"singularity exec ./Assets/covasim_ubuntu.sif python3 Assets/run_sim_sweep.py")
    task = CommandTask(command=command)

    ts = TemplatedSimulations(base_task=task)
    # Add our image
    task.common_assets.add_assets(AssetCollection.from_id_file("covasim.id"))
    sb = SimulationBuilder()
    # Add sweeps on 3 parameters. Total of 1680 simulations(6x14x21)
    sb.add_sweep_definition(partial(set_value, name="pop_size"), [10000, 20000])
    sb.add_sweep_definition(partial(set_value, name="pop_infected"), [10, 100, 1000])
    sb.add_sweep_definition(partial(set_value, name="n_days"), [100, 110, 120])
    sb.add_sweep_definition(partial(set_value, name="rand_seed"), [1234, 4567])
    # add file to each simulation
    sb.add_sweep_definition(partial(default_add_workerorder_sweep_callback, file_name="WorkOrder.json"),
                            "./WorkOrder_orig.json")
    ts.add_builder(sb)
    experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])
    experiment.add_asset(os.path.join("inputs", "run_sim_sweep.py"))
    experiment.add_asset(os.path.join("inputs", "sim_to_inset.py"))
    experiment.run(wait_until_done=True, scheduling=True)
    if experiment.succeeded:
        experiment.to_id_file("run_sim_sweep_scheduling.id")
