"""
Scenario-Based Sweeps, Organize sweeps by scenarios.

This example shows how to run a parameter sweep and automatically
run analysis after all simulations complete.
# We need to run this inside singularity since COMPS does not have some packages plot needs
"""
from itertools import product
import numpy as np

from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

# Create COMPS platform
platform = Platform("SlurmStage")  # or "COMPS", "Calculon", etc.
sif_name = "python_minimal.sif"
# Create base task for simulations
# First, create command for SingularityJSONConfiguredPythonTask's provided_command
command = CommandLine(
    f"singularity exec ./Assets/{sif_name} python3 Assets/run_model_and_plot.py",
)
task = SingularityJSONConfiguredPythonTask(provided_command=command, script_path="inputs/run_model_and_plot.py")
# Add Singularity as COMPS assets
task.common_assets.add_assets(AssetCollection.from_id_file(f"../singularity/definitions/{sif_name}.id"))  # Upload sif id 3eec2bb7-250c-f111-9318-f0921c167864 in comps2
# Add model.py which run_model_and_plot.py needed.
# Note, run_model_and_plot.py will auto upload to comps with SingularityJSONConfiguredPythonTask
task.transient_assets.add_asset("inputs/sir-model-config.py")

# Define scenarios
scenarios = {
    "baseline": {
        "intervention": False,
        "beta": [0.5, 0.6, 0.7],
        "gamma": [0.1, 0.15],
        "description": "No intervention"
    },
    "masks": {
        "intervention": True,
        "beta": [0.3, 0.4, 0.5],  # Reduced transmission
        "gamma": [0.1, 0.15],
        "description": "Mask mandate"
    },
    "lockdown": {
        "intervention": True,
        "beta": [0.1, 0.2, 0.3],  # Strongly reduced
        "gamma": [0.1, 0.15],
        "description": "Full lockdown"
    },
    "vaccination": {
        "intervention": True,
        "beta": [0.5, 0.6, 0.7],
        "gamma": [0.2, 0.3, 0.4],  # Increased recovery
        "description": "Vaccination campaign"
    }
}

# Generate parameter combinations per scenario
all_params = []

for scenario_name, scenario_config in scenarios.items():
    betas = scenario_config["beta"]
    gammas = scenario_config["gamma"]

    for beta, gamma in product(betas, gammas):
        param_dict = {
            "scenario": scenario_name,
            "description": scenario_config["description"],
            "intervention": scenario_config["intervention"],
            "beta": beta,
            "gamma": gamma,
            "R0": beta / gamma
        }
        all_params.append(param_dict)

print(f"Total parameter sets across scenarios: {len(all_params)}")

def set_scenario_params(simulation, params):
    simulation.task.set_parameter("beta", params["beta"])
    simulation.task.set_parameter("gamma", params["gamma"])
    simulation.task.set_parameter("intervention", params["intervention"])
    simulation.tags = params
    simulation.name = f"{params['scenario']}_beta{params['beta']:.2f}"

builder = SimulationBuilder()
builder.add_sweep_definition(set_scenario_params, all_params)

experiment = Experiment.from_builder(
    builder,
    task,
    name="Scenario-Based Sweep"
)
print(f"Created {len(experiment.simulations)} simulations")
print("\nRunning experiment on COMPS...")

# Run experiment
experiment.run(platform=platform, wait_until_done=True)

print(f"\nExperiment ID: {experiment.id}")
print(f"Status: {experiment.status}")

