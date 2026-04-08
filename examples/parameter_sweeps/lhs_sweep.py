"""
Latin Hypercube Sampling Sweep with Automated Analysis on COMPS.

This example shows how to run a parameter sweep and automatically
run analysis after all simulations complete.
# We need to run this inside singularity since COMPS does not have some packages plot needs
"""

from scipy.stats import qmc
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
# Define number of parameters and samples
n_params = 4
n_samples = 100

# Create Latin Hypercube sampler
sampler = qmc.LatinHypercube(d=n_params)
sample = sampler.random(n=n_samples)

# Define parameter bounds
param_bounds = {
    "beta": (0.1, 0.9),
    "gamma": (0.05, 0.3),
    "population": (1000, 100000),
    "days": (100, 365)
}

# Scale samples to parameter ranges
bounds_lower = [param_bounds["beta"][0], param_bounds["gamma"][0],
                param_bounds["population"][0], param_bounds["days"][0]]
bounds_upper = [param_bounds["beta"][1], param_bounds["gamma"][1],
                param_bounds["population"][1], param_bounds["days"][1]]

scaled_samples = qmc.scale(sample, bounds_lower, bounds_upper)

# Convert to list of dicts
param_sets = []
param_names = list(param_bounds.keys())
for sample_vals in scaled_samples:
    param_dict = {name: val for name, val in zip(param_names, sample_vals)}
    # Round population and duration to integers
    param_dict["population"] = int(param_dict["population"])
    param_dict["days"] = int(param_dict["days"])
    param_sets.append(param_dict)

def set_lhs_params(simulation, params):
    for key, value in params.items():
        simulation.task.set_parameter(key, value)

    simulation.tags.update(params)
    simulation.tags["R0"] = params["beta"] / params["gamma"]
    simulation.name = f"LHS_sample_{simulation.id}"

builder = SimulationBuilder()
builder.add_sweep_definition(set_lhs_params, param_sets)

experiment = Experiment.from_builder(
    builder,
    task,
    name="Latin Hypercube Sampling"
)
print(f"Created {len(experiment.simulations)} simulations")
print("\nRunning experiment on COMPS...")

# Run experiment
experiment.run(platform=platform, wait_until_done=True)

print(f"\nExperiment ID: {experiment.id}")
print(f"Status: {experiment.status}")

