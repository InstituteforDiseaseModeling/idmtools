import os

from functools import partial

from idmtools.assets import AssetCollection, Asset
from idmtools.builders import SweepArm, ArmType, ArmExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools_models.dtk.defaults.DTKSIR import DTKSIR
from config_update_parameters import config_update_params
from idmtools_models.dtk import DTKExperiment
from idmtools.core.PlatformFactory import PlatformFactory

current_directory = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.join(current_directory, "bin")
INPUT_PATH = os.path.join(current_directory, "inputs")

sim_duration = 10   # in years
num_seeds = 5

expname = 'example_arm_sweep_serialization'


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)

if __name__ == "__main__":
    platform = PlatformFactory.create(key='COMPS')

    ac = AssetCollection()
    a = Asset(absolute_path=os.path.join(INPUT_PATH, "single_node_demographics.json"))
    ac.add_asset(a)
    e = DTKExperiment.from_default(expname, default=DTKSIR, eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
    e.add_assets(ac)
    simulation = e.simulation()
    sim = config_update_params(simulation)
    sim.set_parameter("Config_Name", "serializing sim")

    timesteps = [sim_duration * 365]
    sim.set_parameter("Serialization_Type", "TIMESTEP")
    sim.set_parameter("Serialization_Time_Steps", sorted(timesteps))

    start_day = sim.get_parameter("Start_Time")
    last_serialization_day = sorted(timesteps)[-1]
    end_day = start_day + last_serialization_day
    sim.set_parameter("Simulation_Duration", end_day)

    e.base_simulation = sim
    arm = SweepArm(type=ArmType.cross)
    set_Run_Number = partial(param_update, param="Run_Number")
    arm.add_sweep_definition(set_Run_Number, range(num_seeds))

    set_x_Temporary_Larval_Habitat = partial(param_update, param="x_Temporary_Larval_Habitat")
    arm.add_sweep_definition(set_x_Temporary_Larval_Habitat, [0.1, 0.2])

    builder = ArmExperimentBuilder()
    builder.add_arm(arm)
    e.builder = builder
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()

    ###
    # Download analysis
    ###

    from idmtools.analysis.AnalyzeManager import AnalyzeManager
    from idmtools.analysis.DownloadAnalyzer import DownloadAnalyzer

    filenames = ['output\\InsetChart.json']
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path='download-e2eB')]

    obj = platform.get_object(id=em.experiment.uid, level=1)  # level 1 is an 'experiment' (a grouping of run items)
    obj.children = platform.get_objects_by_relationship(object=obj, relationship=platform.CHILD)

    manager = AnalyzeManager(configuration={}, platform=platform, items=obj.children, analyzers=analyzers)
    manager.analyze()
