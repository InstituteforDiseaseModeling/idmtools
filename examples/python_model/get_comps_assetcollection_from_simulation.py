import os

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_models.python.python_experiment import PythonExperiment
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import get_asset_collection_id_for_simulation_id, get_asset_collection_by_id


class setParam:
    def __init__(self, param):
        self.param = param

    def __call__(self, simulation, value):
        return simulation.set_parameter(self.param, value)


# connect to COMPS staging
platform = Platform('COMPS2')

# get comps AssetCollection
# Use existing simulation id
sim_id = "50796602-3433-ea11-a2be-f0921c167861"
collection_id = get_asset_collection_id_for_simulation_id(sim_id)
comps_ac = get_asset_collection_by_id(collection_id)

# convert comps assetcollection to idmtools assetcollection
ac: AssetCollection = platform._assets.to_entity(comps_ac)

# create new python experiment in comps with this assetcollection
python_experiment = PythonExperiment(name="example_get_comps_assetcollection_from_simulation",
                                     model_path=os.path.join(COMMON_INPUT_PATH, "compsplatform", "working_model.py"),
                                     assets=ac)

# sweep parameter
builder = ExperimentBuilder()
builder.add_sweep_definition(setParam("min_x"), range(-2, 0))
builder.add_sweep_definition(setParam("max_x"), range(1, 3))

python_experiment.add_builder(builder)

em = ExperimentManager(experiment=python_experiment, platform=platform)
em.run()
em.wait_till_done()
