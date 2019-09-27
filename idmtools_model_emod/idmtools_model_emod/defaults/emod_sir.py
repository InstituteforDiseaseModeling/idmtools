from typing import Dict

from idmtools_model_emod.defaults.iemod_default import IEMODDefault


class EMODSir(IEMODDefault):
    @staticmethod
    def config() -> Dict:
        return {
            "Acquisition_Blocking_Immunity_Decay_Rate": 0.1,
            "Acquisition_Blocking_Immunity_Duration_Before_Decay": 60,
            "Age_Initialization_Distribution_Type": "DISTRIBUTION_SIMPLE",
            "Animal_Reservoir_Type": "NO_ZOONOSIS",
            "Base_Incubation_Period": 0,
            "Base_Individual_Sample_Rate": 1,
            "Base_Infectious_Period": 4,
            "Base_Infectivity": 3.5,
            "Base_Mortality": 0,
            "Base_Population_Scale_Factor": 1,
            "Birth_Rate_Dependence": "POPULATION_DEP_RATE",
            "Birth_Rate_Time_Dependence": "NONE",
            "Burnin_Cache_Mode": "none",
            "Burnin_Cache_Period": 0,
            "Burnin_Name": "",
            "Campaign_Filename": "campaign.json",
            "Climate_Model": "CLIMATE_OFF",
            "Config_Name": "01_SIR",
            "Custom_Coordinator_Events": [],
            "Custom_Individual_Events": [],
            "Custom_Node_Events": [],
            "Custom_Reports_Filename": "NoCustomReports",
            "Default_Geography_Initial_Node_Population": 1000,
            "Default_Geography_Torus_Size": 10,
            "Demographics_Filenames": [
                "generic_scenarios_demographics.json"
            ],
            "Enable_Default_Reporting": 1,
            "Enable_Default_Shedding_Function": 1,
            "Enable_Demographics_Birth": 0,
            "Enable_Demographics_Builtin": 0,
            "Enable_Demographics_Gender": 1,
            "Enable_Demographics_Other": 0,
            "Enable_Demographics_Reporting": 1,
            "Enable_Disease_Mortality": 0,
            "Enable_Heterogeneous_Intranode_Transmission": 0,
            "Enable_Immune_Decay": 0,
            "Enable_Immunity": 1,
            "Enable_Infectivity_Reservoir": 0,
            "Enable_Initial_Prevalence": 0,
            "Enable_Initial_Susceptibility_Distribution": 0,
            "Enable_Interventions": 1,
            "Enable_Maternal_Transmission": 0,
            "Enable_Property_Output": 0,
            "Enable_Skipping": 0,
            "Enable_Spatial_Output": 0,
            "Enable_Strain_Tracking": 0,
            "Enable_Superinfection": 0,
            "Enable_Termination_On_Zero_Total_Infectivity": 0,
            "Enable_Vital_Dynamics": 0,
            "Geography": "SamplesInput",
            "Immunity_Acquisition_Factor": 0,
            "Immunity_Initialization_Distribution_Type": "DISTRIBUTION_OFF",
            "Immunity_Mortality_Factor": 0,
            "Immunity_Transmission_Factor": 0,
            "Incubation_Period_Constant": 0,
            "Incubation_Period_Distribution": "CONSTANT_DISTRIBUTION",
            "Individual_Sampling_Type": "TRACK_ALL",
            "Infection_Updates_Per_Timestep": 1,
            "Infectious_Period_Exponential": 4,
            "Infectious_Period_Distribution": "EXPONENTIAL_DISTRIBUTION",
            "Infectivity_Scale_Type": "CONSTANT_INFECTIVITY",
            "Job_Node_Groups": "Chassis08",
            "Job_Priority": "BELOWNORMAL",
            "Listed_Events": [],
            "Load_Balance_Filename": "",
            "Local_Simulation": 0,
            "Maternal_Transmission_Probability": 0,
            "Max_Individual_Infections": 1,
            "Max_Node_Population_Samples": 40,
            "Migration_Model": "NO_MIGRATION",
            "Minimum_Adult_Age_Years": 15,
            "Mortality_Blocking_Immunity_Decay_Rate": 0.001,
            "Mortality_Blocking_Immunity_Duration_Before_Decay": 60,
            "Mortality_Time_Course": "DAILY_MORTALITY",
            "Node_Grid_Size": 0.042,
            "Num_Cores": 1,
            "Number_Basestrains": 1,
            "Number_Substrains": 1,
            "PKPD_Model": "FIXED_DURATION_CONSTANT_EFFECT",
            "Population_Density_C50": 30,
            "Population_Density_Infectivity_Correction": "CONSTANT_INFECTIVITY",
            "Population_Scale_Type": "USE_INPUT_FILE",
            "Post_Infection_Acquisition_Multiplier": 0,
            "Post_Infection_Mortality_Multiplier": 0,
            "Post_Infection_Transmission_Multiplier": 0,
            "Report_Coordinator_Event_Recorder": 0,
            "Report_Event_Recorder": 0,
            "Report_Node_Event_Recorder": 0,
            "Report_Surveillance_Event_Recorder": 0,
            "Run_Number": 1,
            "Sample_Rate_0_18mo": 1,
            "Sample_Rate_10_14": 1,
            "Sample_Rate_15_19": 1,
            "Sample_Rate_18mo_4yr": 1,
            "Sample_Rate_20_Plus": 1,
            "Sample_Rate_5_9": 1,
            "Sample_Rate_Birth": 1,
            "Serialization_Type": "NONE",
            "Simulation_Duration": 90,
            "Simulation_Timestep": 1,
            "Simulation_Type": "GENERIC_SIM",
            "Start_Time": 0,
            "Susceptibility_Scale_Type": "CONSTANT_SUSCEPTIBILITY",
            "Symptomatic_Infectious_Offset": 0,
            "Transmission_Blocking_Immunity_Decay_Rate": 0.1,
            "Transmission_Blocking_Immunity_Duration_Before_Decay": 60,
            "x_Air_Migration": 1,
            "x_Birth": 1,
            "x_Local_Migration": 1,
            "x_Other_Mortality": 1,
            "x_Population_Immunity": 1,
            "x_Regional_Migration": 1,
            "x_Sea_Migration": 1,
            "x_Temporary_Larval_Habitat": 1
        }

    @staticmethod
    def campaign() -> Dict:
        return {
            "Campaign_Name": "Initial Seeding",
            "Events": [
                {
                    "Event_Coordinator_Config": {
                        "Demographic_Coverage": 0.0005,
                        "Intervention_Config": {
                            "Outbreak_Source": "PrevalenceIncrease",
                            "class": "OutbreakIndividual"
                        },
                        "class": "StandardInterventionDistributionEventCoordinator"
                    },
                    "Event_Name": "Outbreak",
                    "Nodeset_Config": {
                        "class": "NodeSetAll"
                    },
                    "class": "CampaignEvent"
                }
            ],
            "Use_Defaults": 1
        }

    @staticmethod
    def demographics() -> Dict:
        return {"generic_scenarios_demographics.json": {
            "Metadata": {
                "DateCreated": "Sun Sep 25 23:19:55 2011",
                "Tool": "convertdemog.py",
                "Author": "jsteinkraus",
                "IdReference": "0",
                "NodeCount": 1,
                "Resolution": 150
            },
            "Defaults": {
            },
            "Nodes": [
                {
                    "NodeID": 1,
                    "NodeAttributes": {
                        "Latitude": 0,
                        "Longitude": 0,
                        "Altitude": 0,
                        "Airport": 0,
                        "Region": 1,
                        "Seaport": 0,
                        "InitialPopulation": 10000,
                        "BirthRate": 0.0000548
                    },
                    "IndividualAttributes": {
                        "AgeDistributionFlag": 3,
                        "AgeDistribution1": 0.000118,
                        "AgeDistribution2": 0,
                        "PrevalenceDistributionFlag": 0,
                        "PrevalenceDistribution1": 0.0,
                        "PrevalenceDistribution2": 0.0,
                        "SusceptibilityDistributionFlag": 0,
                        "SusceptibilityDistribution1": 1,
                        "SusceptibilityDistribution2": 0,
                        "RiskDistributionFlag": 0,
                        "RiskDistribution1": 1,
                        "RiskDistribution2": 0,
                        "MigrationHeterogeneityDistributionFlag": 0,
                        "MigrationHeterogeneityDistribution1": 1,
                        "MigrationHeterogeneityDistribution2": 0,
                        "MortalityDistribution": {
                            "NumDistributionAxes": 2,
                            "AxisNames": ["gender", "age"],
                            "AxisUnits": ["male=0,female=1", "years"],
                            "AxisScaleFactors": [1, 365],
                            "NumPopulationGroups": [2, 1],
                            "PopulationGroups": [
                                [0, 1],
                                [0]
                            ],
                            "ResultUnits": "deaths per day",
                            "ResultScaleFactor": 1,
                            "ResultValues": [
                                [0.0000548],
                                [0.0000548]
                            ]
                        }
                    }
                }
            ]
        }}
