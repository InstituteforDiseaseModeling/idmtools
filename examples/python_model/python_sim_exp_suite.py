import os
import sys
from functools import partial
from typing import Any, Dict

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask

platform = Platform('CALCULON')

parameters = {'b' + str(x): x**2 for x in (2, 4, 6)}
task = JSONConfiguredPythonTask(script_path=os.path.join("inputs", "python_model_with_deps", "Assets", "model.py"),
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
exp.assets.add_directory(assets_directory=os.path.join("inputs", "python_model_with_deps", "Assets"))
# create suite
suite = Suite(name='Idm Suite')
suite.update_tags({'name': 'suite_tag', 'idmtools': '123'})
platform.create_items([suite])
# add experiment to suite
suite.add_experiment(exp)
# you can also add the experiment to a suite like this:
# exp.suite = suite

# run suite
#platform.run_items(items=suite, wait_until_done=True)
suite.run(wait_until_done=True)
sys.exit(0 if suite.succeeded else -1)



