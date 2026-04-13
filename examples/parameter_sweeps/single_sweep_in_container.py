"""
Parameter Sweep with Automated Analysis on COMPS

This example shows how to run a parameter sweep and automatically
run analysis after all simulations complete.
"""
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder
from idmtools_models.python.python_task import PythonTask

# Create COMPS platform
platform = Platform("Container", job_directory="DEST") # or "COMPS", "Calculon", etc.

# Create base task for simulations
# command = CommandLine(
#     f"singularity exec ./Assets/python_analysis.sif python3 Assets/run_model_and_plot.py",
# )
task = PythonTask(script_path="inputs/run_model_and_plot.py")
task.transient_assets.add_asset("inputs/sir-model-config.py")

# Set base parameters
task.parameters = {
    "gamma": 0.1,
    "days": 160,
    "population": 10000
}

# Create builder for parameter sweep
builder = SimulationBuilder()

# Sweep over transmission rate (beta)
beta_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

def set_beta_parameter(simulation, beta):
    """Set beta parameter for the simulation."""
    simulation.task.parameters["beta"] = beta
    simulation.tags["beta"] = beta

builder.add_sweep_definition(set_beta_parameter, beta_values)

# Create experiment from builder
experiment = Experiment.from_builder(
    builder,
    task,
    name="Single Parameter Sweep with Analysis"
)

print(f"Created {len(experiment.simulations)} simulations")
print("\nRunning experiment on COMPS...")

# Run experiment
experiment.run(platform=platform, wait_until_done=True)

print(f"\nExperiment ID: {experiment.id}")
print(f"Status: {experiment.status}")

