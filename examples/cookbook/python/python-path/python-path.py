import os

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.python_task import PythonTask
from idmtools_models.templated_script_task import TemplatedScriptTask, get_script_wrapper_unix_task, LINUX_PYTHON_PATH_WRAPPER


platform = Platform("CALCULON")
# This task can be anytype of task that would run python. Here we are running a simple model script that consumes the example
# package "a_package"
task = PythonTask(script_path="model.py", python_path='python3.7')
# add our library. On Comps, you could use RequirementsToAssetCollection as well
task.common_assets.add_asset("a_package.py")
# we request a wrapper script for Unix. The wrapper should match the computation platform's OS
# We also use the built-it LINUX_PYTHON_PATH_WRAPPER template which modifies our PYTHONPATH to load libraries from Assets/site-packages and Assets folders
wrapper_task: TemplatedScriptTask = get_script_wrapper_unix_task(task, template_content=LINUX_PYTHON_PATH_WRAPPER)
# we have to set the bash path remotely
wrapper_task.script_binary = "/bin/bash"

# Now we define our experiment. We could just as easily use this wrapper in a templated simulation builder as well
experiment = Experiment.from_task(name=os.path.basename(__file__), task=wrapper_task)
experiment.run(wait_until_done=True)
