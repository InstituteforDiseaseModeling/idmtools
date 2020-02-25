# example to use CommandTask to generate n simulations

import json
import os
import sys
from functools import partial

from idmtools.assets import Asset
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_test import COMMON_INPUT_PATH

DEFAULT_INPUT_PATH = os.path.join(COMMON_INPUT_PATH)
DEFAULT_ERADICATION_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod", "Eradication.exe")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod_files", "config.json")
DEFAULT_CAMPAIGN_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod_files", "campaign.json")
DEFAULT_DEMO_PATH = os.path.join(DEFAULT_INPUT_PATH, "emod_files", "demographics.json")


def generate_experiment():
    command = "Assets/Eradication.exe --config config.json --input-path ./Assets"
    task = CommandTask(command=command)
    with open(DEFAULT_CONFIG_PATH, 'r') as cin:
        task.config = json.load(cin)
        # task.config["parameters"]["Demographics_Filenames"][0] = "Assets/" + task.config["parameters"]["Demographics_Filenames"][0]
        task.config["parameters"]["Campaign_Filename"] = "Assets/" + task.config["parameters"]["Campaign_Filename"]
        task.config["parameters"]["Enable_Immunity"] = 1

    def save_config(task):
        return Asset(filename='config.json', content=json.dumps(task.config))

    task.gather_transient_asset_hooks.append(save_config)
    #task.transient_assets.add_asset(save_config(task))

    def update_param(simulation, param, value):
        simulation.task.config[param] = value
        return {param: value}

    # add eradication.exe to current dir in comps
    eradication_asset = Asset(absolute_path=DEFAULT_ERADICATION_PATH)
    task.common_assets.add_asset(eradication_asset)

    # add config.json/campaign/demographic.json to current dir in comps
    campaign_asset = Asset(absolute_path=DEFAULT_CAMPAIGN_PATH)
    demo_asset = Asset(absolute_path=DEFAULT_DEMO_PATH)

    task.common_assets.add_asset(campaign_asset)
    task.common_assets.add_asset(demo_asset)

    builder = SimulationBuilder()
    # Now add our sweep on a list
    set_run_number = partial(update_param, param="Run_Number")
    builder.add_sweep_definition(set_run_number, range(0, 2))
    # create experiment from task
    experiment = Experiment.from_builder(builder, task, name="example--emod_from_builder.py")

    platform.run_items(experiment)
    platform.wait_till_done(experiment)
    return experiment


if __name__ == "__main__":
    platform = Platform('COMPS2')
    experiment = generate_experiment()
    sys.exit(0 if experiment.succeeded else -1)
