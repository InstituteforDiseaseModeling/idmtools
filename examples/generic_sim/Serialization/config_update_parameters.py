from idmtools_model_emod import EMODSimulation


def param_update(simulation: 'EMODSimulation', param, value):
    return simulation.set_parameter(param, value)


def standard_cb_updates(sim: 'EMODSimulation'):
    sim.update_parameters({
        # DEMOGRAPHICS
        "Birth_Rate_Dependence": "POPULATION_DEP_RATE",
        "Demographics_Filenames": [
            "demographics.json"
        ],
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


def config_update_params(sim):
    # General
    standard_cb_updates(sim)
    return sim
