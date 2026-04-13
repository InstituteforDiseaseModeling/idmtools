"""
Two-Dimensional Grid Sweep with Automated Analysis on COMPS.

This example shows how to run a parameter sweep and automatically
run analysis after all simulations complete.
# We need to run this inside singularity since COMPS does not have some packages plot needs
"""
from itertools import product
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

# Set base parameters
task.parameters = {
    "gamma": 0.1,
    "days": 160,
    "population": 10000
}

# Create builder for parameter sweep
builder = SimulationBuilder()

# Define parameter ranges
beta_values = [0.3, 0.4, 0.5, 0.6, 0.7]
gamma_values = [0.05, 0.1, 0.15, 0.2]

# Create all combinations
combinations = list(product(beta_values, gamma_values))

def set_params(simulation, params):
    beta, gamma = params
    simulation.task.set_parameter("beta", beta)
    simulation.task.set_parameter("gamma", gamma)
    simulation.tags["beta"] = beta
    simulation.tags["gamma"] = gamma
    simulation.tags["R0"] = beta / gamma
    simulation.name = f"beta_{beta:.2f}_gamma_{gamma:.2f}"


builder.add_sweep_definition(set_params, combinations)

# Create experiment from builder
experiment = Experiment.from_builder(
    builder,
    task,
    name="Single Parameter Sweep with Analysis"
)

print(f"Created {len(experiment.simulations)} simulations")
print("\nRunning experiment on COMPS...")

# Creates 5 × 4 = 20 simulations
experiment = Experiment.from_builder(builder, task, name="2D Grid Sweep")
print(f"Created {len(experiment.simulations)} simulations")
print("\nRunning experiment on COMPS...")

# Run experiment
experiment.run(platform=platform, wait_until_done=True)

print(f"\nExperiment ID: {experiment.uid}")
print(f"Status: {experiment.status}")

