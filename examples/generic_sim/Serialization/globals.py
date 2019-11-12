import os
import shutil
import typing
from functools import partial

import pandas as pd

from idmtools.builders import ExperimentBuilder

if typing.TYPE_CHECKING:
    from idmtools_model_emod import EMODSimulation

current_directory = os.path.dirname(os.path.realpath(__file__))
BIN_PATH = os.path.abspath(os.path.join(current_directory, "bin"))
INPUT_PATH = os.path.abspath(os.path.join(current_directory, "inputs"))

SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "01_write_file_singlenode", "outputs"))
if os.path.exists(SERIALIZATION_PATH):
    random_sim_id = os.listdir(SERIALIZATION_PATH)[-1]
    SERIALIZATION_PATH = os.path.join(SERIALIZATION_PATH, random_sim_id)

MULTINODE_SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "04_write_file_multinode", "outputs"))
if os.path.exists(MULTINODE_SERIALIZATION_PATH):
    multinode_random_sim_id = os.listdir(MULTINODE_SERIALIZATION_PATH)[-1]
    MULTINODE_SERIALIZATION_PATH = os.path.join(MULTINODE_SERIALIZATION_PATH, multinode_random_sim_id)

MULTICORE_SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "06_write_file_multicore", "outputs"))
if os.path.exists(MULTICORE_SERIALIZATION_PATH):
    multicore_random_sim_id = os.listdir(MULTICORE_SERIALIZATION_PATH)[-1]
    MULTICORE_SERIALIZATION_PATH = os.path.join(MULTICORE_SERIALIZATION_PATH, multicore_random_sim_id)

MIGRATION_SERIALIZATION_PATH = os.path.abspath(os.path.join(current_directory, "08_write_file_migration", "outputs"))
if os.path.exists(MIGRATION_SERIALIZATION_PATH):
    migration_random_sim_id = os.listdir(MIGRATION_SERIALIZATION_PATH)[-1]
    MIGRATION_SERIALIZATION_PATH = os.path.join(MIGRATION_SERIALIZATION_PATH, migration_random_sim_id)

START_DAY = 0
SIMULATION_DURATION = 120
REPETITIONS = 4
NUM_CORES = 4
LAST_SERIALIZATION_DAY = 70
PRE_SERIALIZATION_DAY = 50


def param_update(simulation: 'EMODSimulation', param, value):
    return simulation.set_parameter(param, value)


def get_seed_experiment_builder():
    builder = ExperimentBuilder()
    set_Run_Number = partial(param_update, param="Run_Number")
    builder.add_sweep_definition(set_Run_Number, range(REPETITIONS))
    return builder


def load_csv_file(filename, dir=None):
    df = None
    if dir:
        filepath = os.path.join(dir, filename)
    else:
        filepath = os.path.join(os.path.curdir, filename)

    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    return df


def del_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def config_update_params(sim: 'EMODSimulation'):
    sim.update_parameters({
        # DEMOGRAPHICS
        "Birth_Rate_Dependence": "POPULATION_DEP_RATE",
        "Enable_Birth": 0,
        "Enable_Demographics_Reporting": 1,
        "Enable_Initial_Prevalence": 1,
        "Enable_Strain_Tracking": 0,
        "Enable_Termination_On_Zero_Total_Infectivity": 0,
        "Enable_Vital_Dynamics": 0,
        "Enable_Immune_Decay": 0,
        "Post_Infection_Acquisition_Multiplier": 0.7,
        "Post_Infection_Transmission_Multiplier": 0.4,
        "Post_Infection_Mortality_Multiplier": 0.3,
        "Enable_Maternal_Protection": 0,
        "Enable_Infectivity_Scaling": 0,

        # DISEASE
        "Base_Incubation_Period": 0,
        "Base_Infectivity": 0.7,

        # PRIMARY
        "Config_Name": "Generic serialization 01 writes files",
        "Geography": "SamplesInput",
        "Run_Number": 1,
        "Simulation_Duration": 120,
        "Start_Time": 0
    })
