import typing

if typing.TYPE_CHECKING:
    from typing import List
    from idmtools_model_emod import EMODSimulation


def enable_serialization(simulation: 'EMODSimulation', use_absolute_times: 'bool' = False):
    if use_absolute_times:
        simulation.set_parameter("Serialization_Type", "TIME")
    else:
        simulation.set_parameter("Serialization_Type", "TIMESTEP")  # Note: This should work in both 2.18 and 2.20


def add_serialization_timesteps(simulation: 'EMODSimulation', timesteps: 'List[int]',
                                end_at_final: 'bool' = False, use_absolute_times: 'bool' = False):
    """
        Serialize the population of this simulation at specified timesteps.
        If the simulation is run on multiple cores, multiple files will be created.
    Args:
        simulation: An EMODSimulation
        timesteps: Array of integers representing the timesteps to use
        end_at_final: (False) set the simulation duration such that the last serialized_population file ends the
                       simulation. NOTE: may not work if timestep size is not 1
        use_absolute_times: (False) method will define simulation times instead of timesteps see documentation on
                            "Serialization_Type" for details

    Returns:

    """
    enable_serialization(simulation, use_absolute_times)

    # Set the timesteps
    if not use_absolute_times:
        simulation.set_parameter("Serialization_Time_Steps", sorted(timesteps))
    else:
        simulation.set_parameter("Serialization_Times", sorted(timesteps))

    if end_at_final:
        start_day = simulation.get_parameter("Start_Time")
        last_serialization_day = sorted(timesteps)[-1]
        end_day = start_day + last_serialization_day
        simulation.set_parameter("Simulation_Duration", end_day)


def load_serialized_population(simulation: 'EMODSimulation', population_path: 'str', population_filenames: 'List[str]'):
    """
        Sets simulation to load a serialized population from the filesystem
    Args:
        simulation: An EMODSimulation
        population_path: relative path from the working directory to the location of the serialized population files.
        population_filenames: names of files in question

    Returns:

    """
    simulation.update_parameters({"Serialized_Population_Path": population_path,
                                  "Serialized_Population_Filenames": population_filenames})
