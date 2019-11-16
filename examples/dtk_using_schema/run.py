import json
import re
from collections import ChainMap

from idmtools.builders import ExperimentBuilder
from idmtools.core.platform_factory import Platform
from idmtools.managers import ExperimentManager
from idmtools_model_emod import EMODExperiment, IEMODDefault


class SchemaDefault(IEMODDefault):
    GENERIC_SIM = ["SerializationTimeCalc", "Simulation", "Node", "NodeDemographics", "Individual", "Susceptibility",
                   "Infection", "GENERIC_SIM"]
    VECTOR_SIM = [*GENERIC_SIM, "Vector.Susceptibility", "VECTOR_SIM"]
    MALARIA_SIM = [*VECTOR_SIM, "Malaria.Individual", "Malaria.Infection", "Malaria.Susceptibility", "MALARIA_SIM"]

    def __init__(self, schema_path="schema.json", components=None, simulation_type=None, manual_fixes=None):

        # Load the schema
        with open(schema_path, 'r') as fp:
            schema = json.load(fp)
            self.schema_config = schema["config"]

        # Config components
        self.parameters_info = ChainMap(*[self.schema_config[component] for component in reversed(components)])

        # Remove the components without default
        self.parameters_info = {k: v for k, v in self.parameters_info.items() if "default" in v}

        # Create the default config
        self.default_config = {param: self._get_default(param_config) for param, param_config in
                               self.parameters_info.items()}

        # Set the fixes
        self.default_config.update(manual_fixes)
        self.default_config["Simulation_Type"] = simulation_type

        # Resolve dependencies
        self._resolve_dependencies()

    @staticmethod
    def _get_default(param_info):
        default = param_info.get("default", None)

        if default == "UNINITIALIZED STRING":
            return ""

        return default

    def _delete_param(self, dependencies):
        for depends_on_param, depends_on_value in dependencies.items():
            # If we do not find the dependent parameter in the config -> delete this one
            if depends_on_param not in self.default_config:
                print(f"{depends_on_param} not present in configuration")
                return True

            # Retrieve the value in the config
            config_value = self.default_config[depends_on_param]

            # Compare
            if config_value == depends_on_value:
                continue

            # Handle strings
            if isinstance(depends_on_value, str):
                trimmed = re.sub(r"\s+", "", depends_on_value)
                if "," in trimmed and config_value in trimmed.split(","):
                    continue

                if str(config_value) == depends_on_value:
                    continue

            print(f"Did not satisfied dependency: {depends_on_param}={depends_on_value} (actual: {config_value})")
            return True

        return False

    def _resolve_dependencies(self):
        for p, info in self.parameters_info.items():
            if "depends-on" in info and self._delete_param(info["depends-on"]):
                print(f"Deleting {p}")
                del self.default_config[p]

    def config(self):
        return self.default_config

    def campaign(self):
        return {
            "Campaign_Name": "Initial Seeding",
            "Events": [
            ],
            "Use_Defaults": 1
        }

    def demographics(self):
        return {
            "demo.json": {
                "Metadata": {
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
            }
        }


if __name__ == "__main__":
    defaults = SchemaDefault(components=SchemaDefault.VECTOR_SIM, simulation_type="VECTOR_SIM",
                             manual_fixes={"Number_Substrains": 1})
    platform = Platform("COMPS2")

    e = EMODExperiment.from_default("test_from_default", default=defaults,
                                    eradication_path="./Eradication-malaria-ongoing.exe")


    def param_a_update(simulation, value):
        simulation.set_parameter("Run_Number", value)
        return {"Run_Number": value}


    builder = ExperimentBuilder()
    # Sweep parameter "Run_Number"
    builder.add_sweep_definition(param_a_update, range(3))
    e.builder = builder
    em = ExperimentManager(experiment=e, platform=platform)
    em.run()
    em.wait_till_done()
