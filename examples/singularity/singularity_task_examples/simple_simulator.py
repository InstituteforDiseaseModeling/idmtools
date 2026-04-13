"""
Example: Using Generic SingularityJSONConfiguredTask

This example demonstrates how to use the generic SingularityJSONConfiguredTask
for non-Python tasks (e.g., R scripts, shell scripts, or compiled binaries).
"""
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_models.singularity_json_task import SingularityJSONConfiguredTask
from idmtools.builders import SimulationBuilder

# Create platform
platform = Platform("SlurmStage")

base_task = SingularityJSONConfiguredTask()
base_task.provided_command = CommandLine(
    "singularity exec ./Assets/python_minimal.sif python3 ./Assets/model.py"
)
base_task.common_assets.add_assets(AssetCollection.from_id_file("../definitions/python_minimal.sif.id"))  # Upload sif id 707985f2-0e09-f111-9318-f0921c167864 in comps2
# Add model.py to Assets
base_task.common_assets.add_asset("model.py")

# Set base parameters
base_task.parameters = {
    "alpha": 0.1,
    "beta": 0.2
}

# Create a builder for parameter sweeps
builder = SimulationBuilder()

# Sweep over alpha parameter
def set_alpha(simulation: Simulation, value):
    #simulation.task.command.add_raw_argument(f"--alpha {value}")
    return simulation.task.set_parameter("alpha", value)


alpha_values = [0.1, 0.2, 0.3, 0.4, 0.5]
builder.add_sweep_definition(set_alpha, alpha_values)

# Create experiment from builder
experiment = Experiment.from_builder(
    builder,
    base_task,
    name="Generic Singularity Parameter Sweep2"
)

print(f"✓ Created parameter sweep with {len(experiment.simulations)} simulations")
print(f"  Alpha values: {alpha_values}")

experiment.run(wait_until_done=True)