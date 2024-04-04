from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment

platform = Platform('CALCULON')
task = CommandTask(command="python --version")
experiment = Experiment.from_task(task=task, name="Example of experiment from task")
experiment.run(wait_until_done=True)
