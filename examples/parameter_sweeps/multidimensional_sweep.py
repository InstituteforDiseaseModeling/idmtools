"""
Multi-Dimensional Sweep with Automated Analysis on COMPS.

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

# Define parameter spaces
params = {
    "beta": np.linspace(0.3, 0.7, 5),
    "gamma": np.linspace(0.05, 0.2, 4),
    "population": [1000, 5000, 10000],
    "initial_infected": [1, 10, 50]
}

# Generate all combinations
combinations = list(product(
    params["beta"],
    params["gamma"],
    params["population"],
    params["initial_infected"]
))

print(f"Total combinations: {len(combinations)}")  # 5×4×3×3 = 180

def set_all_params(simulation, params):
    beta, gamma, pop, init_inf = params

    simulation.task.set_parameter("beta", beta)
    simulation.task.set_parameter("gamma", gamma)
    simulation.task.set_parameter("population", pop)
    simulation.task.set_parameter("initial_infected", init_inf)

    # Tag for easy filtering
    simulation.tags = {
        "beta": beta,
        "gamma": gamma,
        "population": pop,
        "initial_infected": init_inf,
        "R0": beta / gamma
    }

    simulation.name = f"N{pop}_beta{beta:.2f}_gamma{gamma:.2f}_init_inif{init_inf}"

builder = SimulationBuilder()
builder.add_sweep_definition(set_all_params, combinations)

experiment = Experiment.from_builder(
    builder,
    task,
    name="Multi-Dimensional Factorial"
)
print(f"Created {len(experiment.simulations)} simulations")
print("\nRunning experiment on COMPS...")

# Run experiment
experiment.run(platform=platform, wait_until_done=True)

print(f"\nExperiment ID: {experiment.id}")
print(f"Status: {experiment.status}")

