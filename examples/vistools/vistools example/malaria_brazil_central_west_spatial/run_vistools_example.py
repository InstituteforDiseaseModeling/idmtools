import os
from functools import partial

from idmtools.assets import AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools.managers.work_item_manager import WorkItemManager
from idmtools_platform_comps.ssmt_work_items.comps_workitems import VisToolsWorkItem
from idmtools_model_emod import EMODExperiment
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_INPUT_PATH = os.path.join(COMMON_INPUT_PATH, "malaria_brazil_central_west_spatial")
DEFAULT_ERADICATION_PATH = os.path.join(DEFAULT_INPUT_PATH, "Assets", "Eradication.exe")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_INPUT_PATH, "config.json")
DEFAULT_CAMPAIGN_JSON = os.path.join(DEFAULT_INPUT_PATH, "campaign.json")
DEFAULT_DEMOGRAPHICS_JSON = os.path.join(DEFAULT_INPUT_PATH,
                                         "Brazil_Central_West_Brazil_Central_West_2.5arcmin_demographics.json")


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


def generate_sim():
    assets_path = os.path.join(DEFAULT_INPUT_PATH, "Assets")
    ac = AssetCollection.from_directory(assets_directory=assets_path)
    e = EMODExperiment.from_files("vistools test sim",
                                  eradication_path=DEFAULT_ERADICATION_PATH,
                                  config_path=DEFAULT_CONFIG_PATH,
                                  campaign_path=DEFAULT_CAMPAIGN_JSON,
                                  demographics_paths=DEFAULT_DEMOGRAPHICS_JSON)
    e.legacy_exe = True
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
    sim_id = str(sims[0].uid)
    node_type = 'Points'
    data = {"SimulationId": "" + sim_id + "", "NodesRepresentation": node_type}
    tags = {'SimulationId': sim_id}
    wi = VisToolsWorkItem(item_name="vistools", tags=tags, work_order=data, related_simulations=[sim_id])

    wim = WorkItemManager(wi, platform)
    wim.process(check_status=True)

    output_path = "workitem_output"
    out_filenames = ["WorkOrder.json"]
    ret = platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, output_path)
