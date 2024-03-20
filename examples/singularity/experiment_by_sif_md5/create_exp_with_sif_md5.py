# This script is to create python sif singularity container based on the definition file
import copy
import os
import sys
from functools import partial

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_platform_comps.utils.general import generate_ac_from_asset_md5_file
from idmtools_platform_comps.utils.singularity_build import SingularityBuildWorkItem

image_name = "alpine_simple.sif"


def create_singularity_sif(platform):
    # This script is to create python sif singularity container based on the definition file python_singularity.def.
    # if you want to recreate a new sif file, you can set force=True
    def_file = os.path.join('input', 'python_singularity.def')
    sbi = SingularityBuildWorkItem(name="Create my test sif", definition_file=def_file, image_name=image_name, force=False)
    sbi.add_assets(["input/model.py"])
    sbi.tags = dict(image="alpine_simple.sif")
    sbi.run(wait_until_done=True, platform=platform)
    if sbi.succeeded:
        # Write ID file
        sbi.asset_collection.to_id_file("alpine_simple.id")


def create_experiment_with_sif(platform):
    # get the asset collection from the md5 file (asset id of sin
    ac = generate_ac_from_asset_md5_file(platform, f"{image_name}.md5")
    sif_asset = ac.assets[0]
    sif_filename = [
        acf.filename for acf in ac.assets if acf.filename.endswith(".sif")
    ][0]

    task = CommandTask(command="anything")
    task.config = dict(a=1, b=1)
    # define a template for our commands
    command_template = "python3 Assets/model.py --a {a} --b {b}"

    # Define a function that renders our command line as we build simulations
    def create_command_line_hook(simulation, platform):
        # set the command dynamically
        simulation.task.command = f"singularity exec Assets/{sif_filename} " + command_template.format(**simulation.task.config)
        # return configs as tags
        return copy.deepcopy(simulation.task.config)

    # add the pre-creation hook to the task with the command line. we don't have to do this in emod-task since it's already done
    task.add_pre_creation_hook(create_command_line_hook)
    ts = TemplatedSimulations(base_task=task)
    builder = SimulationBuilder()

    def set_parameter(simulation, parameter, value):
        simulation.task.config[parameter] = value
        return {parameter: value}

    # Add sweeps on 2 parameters. a and b
    builder.add_sweep_definition(partial(set_parameter, parameter="a"), range(3))
    builder.add_sweep_definition(partial(set_parameter, parameter="b"), range(3))
    ts.add_builder(builder)
    experiment = Experiment.from_template(ts, name=os.path.split(sys.argv[0])[1])

    task.common_assets.add_asset(sif_asset)
    task.common_assets.add_asset(os.path.join("input", "model.py"))
    experiment.run(platform=platform, wait_until_done=True)


if __name__ == '__main__':
    platform = Platform("SlurmStage")
    # create singularity sif image which will store md5 of singularity sif asset id to the file. Note, this is function
    #
    create_singularity_sif(platform)
    # create experiment with sif's md5 from above step
    create_experiment_with_sif(platform)

