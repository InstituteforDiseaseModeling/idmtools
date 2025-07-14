# This example shows how to use the end-to-end workflow of the IDM tools.
# First run the experiment, then run the ssmt analysis.
# The ssmt analysis will run on the same platform as the experiment and download the results from COMPS to local.
import os
import sys
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from analysis_runner import ssmt_analysis

CURRENT_DIRECTORY = os.path.dirname(__file__)
input_directory = os.path.join(CURRENT_DIRECTORY, "..", "..", "python_model", "inputs")
platform = Platform('Calculon')

parameters = {'b' + str(x): x**2 for x in (2, 4, 6)}
task = JSONConfiguredPythonTask(script_path=os.path.join(input_directory, "python_model_with_deps", "Assets", "model.py"),
                                parameters=parameters)
ts = TemplatedSimulations(base_task=task)
ts.base_simulation.tags['tag1'] = 1

builder = SimulationBuilder()

def param_update(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
    return simulation.task.set_parameter(param, value)


setA = partial(param_update, param="a")
builder.add_sweep_definition(setA, range(3))
ts.add_builder(builder)

exp = Experiment(name=os.path.split(sys.argv[0])[1], simulations=ts)
exp.tags["tag"] = 1
exp.assets.add_directory(assets_directory=os.path.join(input_directory, "python_model_with_deps", "Assets"))
exp.run(wait_until_done=True)

# Run ssmt analysis after the experiment is done. ssmt analysis will run on the same platform as the experiment and download the results to local
ssmt_analysis(exp.id, platform)



