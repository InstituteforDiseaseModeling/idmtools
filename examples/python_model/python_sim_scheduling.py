"""
This example demonstrates how to run a simulation with scheduling using the WorkOrder.json file. The WorkOrder.json file
is used to override the simulation command with the scheduling feature of COMPS. In WorkOrder.json in this example, we
set NumNodes=2. In comps, you can see jobs in each simulation set min_cores and max_cores to 96 and 96 respectively.
(min_cores and max_cores numbers may vary depending on the availability of the resources in the selected nodes)
WorkOrder.json in this exmaple:
{
  "Command": "python3 Assets/model.py",
  "NodeGroupName": "idm_abcd",
  "NumProcesses": 1,
  "NumNodes": 2,
  "Environment": {
    "key1": "value1",
    "key2": "value2",
    "PYTHONPATH": "$PYTHONPATH:$PWD/Assets:$PWD/Assets/site-packages",
    "PATH": "$PATH:$PWD/Assets:$PWD/Assets/site-packages"
  }
}
"""


import os
import sys

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_platform_comps.utils.scheduling import add_work_order


with Platform('CALCULON') as platform:

    # create json config task which generates config.json and add model script comps experiment
    task = JSONConfiguredPythonTask(
        script_path=os.path.join("inputs", "python_model_with_deps", "Assets", "model.py"),
        # set default parameters
        parameters=dict(c=0),
    )
    # create TemplatedSimulations
    ts = TemplatedSimulations(base_task=task)

    # add WorkOrder.json to each simulation as transient_assets
    add_work_order(ts, file_path=os.path.join("inputs", "scheduling", "WorkOrder.json"))

    # create build and define our sweeps
    builder = SimulationBuilder()
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("a"), range(3))
    builder.add_sweep_definition(JSONConfiguredPythonTask.set_parameter_partial("b"), [1, 2])

    # add builder to templatedsimulation
    ts.add_builder(builder)
    # create experiment
    e = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1], tags=dict(tag1=1))
    # run experiment with scheduling
    e.run(wait_until_done=True)
    # use system status as the exit code
    sys.exit(0 if e.succeeded else -1)
