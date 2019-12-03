import os
from functools import partial
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python.python_experiment import PythonExperiment


def param_update(simulation, param, value):
    return simulation.set_parameter(param, 'sweepR04_a_' + str(value) + '.json')


pe = PythonExperiment(name="Allee python model example",
                      model_path=os.path.join("work", "inputs", "allee_python_model", "run_emod_sweep.py"))
pe.base_simulation.envelope = "parameters"
pe.retrieve_python_dependencies()
# pe = PythonExperiment(name="Allee python model example",
#                               model_path=os.path.join("work", "inputs", "allee_python_model", "run_emod_sweep.py"))

pe.tags["tag1"] = "example from allee python model with idmtools"

pe.assets.add_directory(assets_directory=os.path.join("work", "inputs", "allee_python_model"))

setA = partial(param_update, param="infile")


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return param_update(simulation, self.param, value)


builder = ExperimentBuilder()
builder.add_sweep_definition(setA, range(7850, 7855))
pe.base_simulation.set_parameter("fname", "runNsim100.json")
pe.base_simulation.set_parameter("customGrid", 1)
pe.base_simulation.set_parameter("nsims", 100)

pe.builder = builder

# platform = Platform('Local')
platform = Platform('COMPS2', endpoint="https://comps2.idmod.org", environment="Bayesian")

em = ExperimentManager(experiment=pe, platform=platform)
em.run()
