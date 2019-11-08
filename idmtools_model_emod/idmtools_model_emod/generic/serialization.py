from idmtools_model_emod import EMODSimulation


def add_serialization_timesteps(sim: 'EMODSimulation', timesteps: list,
                                end_at_final=False, use_absolute_times=False):
    """
        Serialize the population of this simulation at specified timesteps.
        If the simulation is run on multiple cores, multiple files will be created.
    Args:
        sim: An EMODSimulation
        timesteps: Array of integers representing the timesteps to use
        end_at_final: (False) set the simulation duration such that the last serialized_population file ends the
                       simulation. NOTE: may not work if timestep size is not 1
        use_absolute_times: (False) method will define simulation times instead of timesteps see documentation on
                            "Serialization_Type" for details

    Returns:

    """
    if not use_absolute_times:
        sim.update_parameters({"Serialization_Type": "TIMESTEP",  #Note: This should work in both 2.18 and 2.20
                               "Serialization_Time_Steps": sorted(timesteps)})
    else:
        sim.update_parameters({"Serialization_Type": "TIME",
                               "Serialization_Times": sorted(timesteps)})

    if end_at_final:
        start_day = sim.get_parameter("Start_Time")
        last_serialization_day = sorted(timesteps)[-1]
        end_day = start_day + last_serialization_day
        sim.set_parameter("Simulation_Duration", end_day)


def load_serialized_population(sim: 'EMODSimulation', population_path: str, population_filenames: list):
    """
        Sets simulation to load a serialized population from the filesystem
    Args:
        sim: An EMODSimulation
        population_path: relative path from the working directory to the location of the serialized population files.
        population_filenames: names of files in question

    Returns:

    """
    sim.update_parameters({"Serialized_Population_Path": population_path,
                           "Serialized_Population_Filenames": population_filenames})
