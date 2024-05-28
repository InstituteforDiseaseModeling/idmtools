import os

from idmtools.assets import Asset, AssetCollection
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_comps.ssmt_work_items.comps_workitems import VisToolsWorkItem
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_INPUT_PATH = os.path.join(COMMON_INPUT_PATH, "malaria_brazil_central_west_spatial")
DEFAULT_ERADICATION_PATH = os.path.join(DEFAULT_INPUT_PATH, "Assets", "Eradication.exe")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_INPUT_PATH, "config.json")
DEFAULT_CAMPAIGN_PATH = os.path.join(DEFAULT_INPUT_PATH, "campaign.json")


def generate_sim():
    command = "Eradication.exe --config config.json --input-path ./Assets"
    task = CommandTask(command=command)

    # add Eradication.exe to Assets dir in comps
    # ast = Asset(absolute_path=DEFAULT_ERADICATION_PATH)
    # task.common_assets.add_asset(ast)  #

    # add eradication.exe to current dir in comps
    eradication_asset = Asset(absolute_path=DEFAULT_ERADICATION_PATH)
    task.transient_assets.add_asset(eradication_asset)

    # add config.json to current dir in comps
    config_asset = Asset(absolute_path=DEFAULT_CONFIG_PATH)
    task.transient_assets.add_asset(config_asset)

    # add campaign.json to current dir in comps
    campaign_asset = Asset(absolute_path=DEFAULT_CAMPAIGN_PATH)
    task.transient_assets.add_asset(campaign_asset)

    # add all files from local dir to assetcollection
    assets_path = os.path.join(DEFAULT_INPUT_PATH, "Assets")
    ac = AssetCollection.from_directory(assets_directory=assets_path)

    # create experiment from task
    experiment = Experiment.from_task(task, name="example--run_vistools_example.py", assets=ac)

    experiment.run(wait_until_done=True)

    # return first simulation
    simulations = platform.get_children(experiment.uid, ItemType.EXPERIMENT, force=True)
    return simulations


if __name__ == "__main__":
    platform = Platform('IDMCloud')
    sims = generate_sim()
    sim_id = str(sims[0].uid)
    node_type = 'Points'
    data = {"SimulationId": "" + sim_id + "", "NodesRepresentation": node_type}
    tags = {'SimulationId': sim_id}
    wi = VisToolsWorkItem(item_name="example--run_vistools_example.py", tags=tags, work_order=data, related_simulations=[sim_id])
    wi.run(wait_until_done=True)

    output_path = "workitem_output"
    out_filenames = ["WorkOrder.json"]
    ret = platform.get_files_by_id(wi.uid, ItemType.WORKFLOW_ITEM, out_filenames, output_path)
