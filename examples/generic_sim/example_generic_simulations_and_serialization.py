import os
from functools import partial

from config_update_parameters import config_update_params

from idmtools.builders import ExperimentBuilder, StandAloneSimulationsBuilder
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir
from idmtools_model_emod.generic.serialization import add_serialization_timesteps, load_serialized_population
from idmtools_test import COMMON_INPUT_PATH
from idmtools_test.utils.comps import sims_from_experiment, get_simulation_path

current_directory = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.join(current_directory, "bin")
INPUT_PATH = os.path.join(current_directory, "inputs")

sim_duration = 10  # in years
num_seeds = 5


def param_update(simulation, param, value):
    return simulation.set_parameter(param, value)


if __name__ == "__main__":
    platform = Platform('COMPS')

    # Step1: create experiment and simulation with serialization file in output
    BIN_PATH = os.path.join(COMMON_INPUT_PATH, "serialization")
    sim_duration = 2  # in years
    num_seeds = 1

    expname = 'create_serialization'
    e1 = EMODExperiment.from_default(expname, default=EMODSir(),
                                     eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
    e1.demographics.clear()
    demo_file = os.path.join(COMMON_INPUT_PATH, "serialization", "single_node_demographics.json")
    e1.demographics.add_demographics_from_file(demo_file)

    simulation = e1.base_simulation

    # Update bunch of config parameters
    sim = config_update_params(simulation)
    timesteps = [sim_duration * 365]
    add_serialization_timesteps(simulation=sim, timesteps=[sim_duration * 365],
                                end_at_final=False, use_absolute_times=False)

    start_day = sim.get_parameter("Start_Time")
    last_serialization_day = sorted(timesteps)[-1]
    end_day = start_day + last_serialization_day
    sim.set_parameter("Simulation_Duration", end_day)

    # Sweep parameters
    builder = ExperimentBuilder()
    set_Run_Number = partial(param_update, param="Run_Number")
    builder.add_sweep_definition(set_Run_Number, range(num_seeds))
    e1.tags = {'idmtools': 'create_serialization'}

    set_x_Temporary_Larval_Habitat = partial(param_update, param="x_Temporary_Larval_Habitat")
    builder.add_sweep_definition(set_x_Temporary_Larval_Habitat, [0.1, 0.2])

    # add custom tags with add_sweep_definition
    set_tag = partial(param_update, param="test_tag")
    builder.add_sweep_definition(set_tag, "abcd")

    e1.builder = builder
    em = ExperimentManager(experiment=e1, platform=platform)
    em.run()
    em.wait_till_done()

    # ---------------------------------------------------------------------------------------------
    # Step2: Create new experiment and sim with previous serialized file
    # TODO, ideally we could add new sim to existing exp, but currently we can not do with issue #459

    # First get previous serialized file path
    comps_exp = platform.get_platform_item(item_id=e1.uid, item_type=ItemType.EXPERIMENT)
    comps_sims = sims_from_experiment(comps_exp)
    serialized_file_path = [get_simulation_path(sim) for sim in comps_sims][0]

    # create new experiment
    expname1 = 'reload_serialization'
    e2 = EMODExperiment.from_default(expname1, default=EMODSir(),
                                     eradication_path=os.path.join(BIN_PATH, "Eradication.exe"))
    e2.demographics.clear()
    demo_file = os.path.join(COMMON_INPUT_PATH, "serialization", "single_node_demographics.json")
    e2.demographics.add_demographics_from_file(demo_file)
    e2.tags = {'idmtools': 'reload_serialization'}

    b = StandAloneSimulationsBuilder()

    for i in range(2):
        reload_sim = e2.simulation()
        reload_sim.tags = {"my tag: ": i, "my_other_tag": "test"}  # Adding custom tags
        # reload_sim.config.pop('Serialization_Time_Steps') # Need this step if we use same experiment
        reload_sim.set_parameter("Enable_Immunity", 0)
        reload_sim.set_parameter("Config_Name", "reloading sim")
        reload_sim.set_parameter("Simulation_Duration", sim_duration * 365)
        load_serialized_population(simulation=reload_sim, population_path=os.path.join(serialized_file_path, 'output'),
                                   population_filenames=['state-00730.dtk'])
        b.add_simulation(reload_sim)

    e2.builder = b
    # Ideally we do not need to create another ExperimentManager if we can use same experiment
    em2 = ExperimentManager(experiment=e2, platform=platform)
    em2.run()
    em2.wait_till_done()
