import os
import sys
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.notifiers.microsoft_flow import notify_microsoft_flow_when_done

parameters = {'b' + str(x): x**2 for x in (2, 4, 6)}
bask_task = JSONConfiguredPythonTask(
    script_path=os.path.join("..", "..", "python_model","inputs", "python_model_with_deps", "Assets", "model.py"),
    parameters=parameters)
builder = SimulationBuilder()
builder.add_sweep_definition(bask_task.set_parameter_partial("a"), range(3))
builder.add_sweep_definition(bask_task.set_parameter_partial("b"), [1, 2, 3])

experiment = Experiment.from_builder(builder, base_task=bask_task)
experiment.simulations.base_simulation.name = "abc"
# Add our own custom tag to simulation
experiment.tags["tag1"] = 1
# And maybe some custom Experiment Level Assets
experiment.assets.add_directory(assets_directory=os.path.join("..", "..", "python_model", "inputs", "python_model_with_deps", "Assets"))

platform = Platform('SLURM')
experiment.run()

# Here we define a job to monitor Experiment and let us know it is done
# To configure this job, you need perform this one time for each connection to go to flow.microsoft.com
# 1. Define a new workflow starting from blank
# 2. Select Instant Flow
# 3. Click Skip
# 4. Enter "When an HTTP request is received" and select that item in the search results
# 5. Click "Use Sample Payload to Generate Schema"
# 6. Enter the following json
#    {
#      "message": "Example message",
#      "title" : "Example Title",
#      "url": "http://example.com",
#      "status" : "DONE"
#    }
#  or enter this following schema
# {
#     "type": "object",
#     "properties": {
#         "message": {
#             "type": "string"
#         },
#         "title": {
#             "type": "string"
#         },
#         "url": {
#             "type": "string"
#         },
#         "status": {
#             "type": "string"
#         }
#     }
# }
# 7. Click New Step
# 8. Search for item to connect. I recommend "Send a Mobile Notification". You will need the Microsoft Flow Mobile App(Power Automate) installed
# 9. For text, use the Add dynamic content to add to message. The recommended format is title - message
# 10. Click Save.
# 11. Navigate up to the When a HTTP request is received step and expand. Once expanded, copy the url and use below

url = "https://prod-81.westus.logic.azure.com:443/workflows/4810212b690b457f90bb9eb287261735/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=ViHXsdtZqaVnUQS-j3uqPNgWKO1DkbQrg_QgMXA-jw4"
notify_microsoft_flow_when_done(experiment, message=f"{experiment.name} is Done", url=url)
experiment.wait()
sys.exit(0 if experiment.succeeded else -1)
