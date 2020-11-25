import os
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.python_task import PythonTask
from idmtools_models.templated_script_task import get_script_wrapper_unix_task, LINUX_DICT_TO_ENVIRONMENT


platform = Platform("CALCULON")
# here we define the task we want to use the environment variables. In this example we have a simple python script that prints the EXAMPLE environment variable
task = PythonTask(script_path="model.py")
# Get a task to wrap the script in a shell script. Which get_script_wrapper function you use depends on the platform's OS
wrapper_task = get_script_wrapper_unix_task(
    task=task,
    # and set some values here
    variables=dict(EXAMPLE='It works!')
)
# some platforms need to you hint where their script binary is. Usually this is only applicable to Unix platforms(Linux, Mac, etc)
wrapper_task.script_binary = "/bin/bash"

# Now we define our experiment. We could just as easily use this wrapper in a templated simulation builder as well
experiment = Experiment.from_task(name=os.path.basename(__file__), task=wrapper_task)
experiment.run(wait_until_done=True)
