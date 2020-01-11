import os

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python.python_experiment import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return simulation.set_parameter(self.param, value)


# connect to COMPS staging
platform = Platform('COMPS2')

# get AssetCollection, raw=False means idmtools AssetCollection not Comps AssetCollection
ac: AssetCollection = platform.get_item('bd80dd0c-1b31-ea11-a2be-f0921c167861',
                                                   item_type=ItemType.ASSETCOLLECTION, raw=False)

python_experiment = PythonExperiment(name="example_python_sim_existing_ac",
                                     model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"))

# add the AssetCollection to python experiment
python_experiment.add_assets(ac)

# sweep parameter
builder = ExperimentBuilder()
builder.add_sweep_definition(setParam("min_x"), range(-2, 0))
builder.add_sweep_definition(setParam("max_x"), range(1, 3))

python_experiment.add_builder(builder)

em = ExperimentManager(experiment=python_experiment, platform=platform)
em.run()
em.wait_till_done()
