import os
import typing

from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment
from idmtools_model_emod.defaults import EMODSir

if typing.TYPE_CHECKING:
    from idmtools.entities import IExperiment

CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
INPUT_PATH = os.path.join(CURRENT_DIRECTORY, "inputs")
BIN_PATH = os.path.join(CURRENT_DIRECTORY, "bin")

sim_duration = 10  # in years
num_seeds = 5

expname = 'example_multiple_demographics'

demo_files = [os.path.join(INPUT_PATH, "demographics.json"),
              os.path.join(INPUT_PATH, "PFA_rates_overlay.json"),
              os.path.join(INPUT_PATH, "pfa_simple.json"),
              os.path.join(INPUT_PATH, "uniform_demographics.json")]


def set_simulation_seed(simulation, value):
    return simulation.set_parameter("Run_Number", value)


def experiment_from_files() -> 'IExperiment':
    """
        This function demonstrates the creation of an EMODExperiment from a set of file.
        - Eradication_Path: The path to the executable to run
        - config_path/campaign_path: the paths for config and campaign files,
        automatically loaded to the experiment's base simulation
        - demographics_paths: The demographics files loaded to the experiment demographics

        Notes:
            Because the demographics files are loaded in the experiment, they will be put in the experiment's
            asset collection. All simulations created from this experiment will automatically include those demographics.
            User is free to remove/edit/add new demographics but the ones set in the asset collection are immutable and
            can only be removed.
    """
    e = EMODExperiment.from_files(expname + "_from_files",
                                  eradication_path=os.path.join(INPUT_PATH, "Eradication.exe"),
                                  config_path=os.path.join(INPUT_PATH, "config.json"),
                                  campaign_path=os.path.join(INPUT_PATH, "campaign.json"),
                                  demographics_paths=demo_files)
    return e


def demographics_on_experiment() -> 'IExperiment':
    """
        This function demonstrates the creation of an EMODExperiment from defaults.
        We are then adding the demographics files to the experiment demographics.

        Notes:
            Because the demographics files are loaded in the experiment, they will be put in the experiment's
            asset collection. All simulations created from this experiment will automatically include those demographics.
            User is free to remove/edit/add new demographics but the ones set in the asset collection are immutable and
            can only be removed.
    """

    # Case: load demographics from experiment
    e = EMODExperiment.from_default(expname + "_demo_on_exp", default=EMODSir,
                                    eradication_path=os.path.join(INPUT_PATH, "Eradication.exe"))

    for demog in demo_files:
        e.demographics.add_demographics_from_file(demog)

    return e


def demographics_on_simulation() -> 'IExperiment':
    """
        This function demonstrates the creation of an EMODExperiment from defaults.
        We are then adding the demographics files to the simulation demographics.

        Notes:
            Because the demographics files are loaded in the simulation, they will not be part of the experiment's
            asset collection but will be dumped in the simulation working directory.
            Because they are attached directly to the simulation, the user can modify them freely.
        """

    # Case: load demographics from simulation
    e = EMODExperiment.from_default(expname + "_demo_on_sim", default=EMODSir,
                                    eradication_path=os.path.join(INPUT_PATH, "Eradication.exe"))

    e.base_simulation.load_files(config_path=os.path.join(INPUT_PATH, "config.json"),
                                 campaign_path=os.path.join(INPUT_PATH, "campaign.json"))

    for demog in demo_files:
        e.base_simulation.demographics.add_demographics_from_file(demog)

    return e


if __name__ == "__main__":
    platform = Platform('COMPS')

    # Gather all the functions available for experiment creation
    available_funcs = (experiment_from_files, demographics_on_experiment, demographics_on_simulation)

    # For each of them create a sweep on the seed and run
    for experiment_func in available_funcs:
        e = experiment_func()
        b = ExperimentBuilder()
        b.add_sweep_definition(set_simulation_seed, range(num_seeds))
        e.add_builder(b)
        em = ExperimentManager(experiment=e, platform=platform)
        em.run()
        em.wait_till_done()
