
import os
import sys
from functools import partial

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment

def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


def generate_sim():
    current_dir = os.path.dirname(os.path.realpath(__file__))

    assets_path = os.path.join(current_dir, "inputs", "Assets")
    ac = AssetCollection.from_directory(assets_directory=assets_path)
    INPUT_PATH = os.path.join(current_dir, "inputs")
    e = EMODExperiment.from_files(os.path.split(sys.argv[0])[1],
                                  eradication_path=os.path.join(assets_path,"bin","Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, "config.json"),
                                  campaign_path=os.path.join(INPUT_PATH,"camp.json"))
                                  #demographics_paths=os.path.join(INPUT_PATH, "demo.json"))
    demo_file = os.path.join(INPUT_PATH,"demo.json")
    e.base_simulation.demographics.add_demographics_from_file(demo_file)
    e.add_assets(ac)

    builder = ExperimentBuilder()
    set_Run_Number = partial(param_update, param="Run_Number")
    builder.add_sweep_definition(set_Run_Number, range(5))
    e.add_builder(builder)
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()
    simulations = platform.get_children(em.experiment.uid, ItemType.EXPERIMENT, force=True)
    return simulations

if __name__ == "__main__":
    platform = Platform('COMPS2')
    sims = generate_sim()
    for sim in sims:
        print(str(sim.uid))
