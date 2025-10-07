from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations

def update_parameter_callback(simulation, sleep_time):
    simulation.task.command.add_argument(sleep_time)
    return {'sleep_time': sleep_time}

# base command to be executed. This command will sleep for the number of seconds passed as an argument
command = "python3 Assets/sleep.py"
task = CommandTask(command=command)
# add the sleep.py file to the assets
task.common_assets.add_asset("inputs/python_models/sleep.py")
# create a templated simulation with the task
ts = TemplatedSimulations(base_task=task)
# create a simulation builder
sb = SimulationBuilder()
# add a sweep definition to the simulation builder. this will create total 9 simulations with sleep time ranging from 1 to 9
sb.add_sweep_definition(update_parameter_callback, sleep_time=range(1, 10))
ts.add_builder(sb)
# create an experiment from the templated simulation
experiment = Experiment.from_template(ts, name="run_sweep_sleep")
# run the experiment on the platform. wait_until_done=True will wait for the experiment to finish before proceeding
with Platform("Container", job_directory="DEST"):
    experiment.run(wait_until_done=True)