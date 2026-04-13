# run_python_sir.py
from idmtools.assets import AssetCollection
from idmtools.core.platform_factory import Platform
from idmtools.entities import CommandLine
from idmtools.entities.experiment import Experiment
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from idmtools_models.python.singularity_json_python_task import SingularityJSONConfiguredPythonTask

# Create platform
# platform = Platform("Container", job_directory="DEST")
platform = Platform("SlurmStage")

platform_type = platform.__class__.__name__
sif_name = "python_minimal.sif"
## If is Comps platform, we need to run in singularity
if platform_type == 'COMPSPlatform':
    command = CommandLine(
        f"singularity exec ./Assets/{sif_name} python3 Assets/sir_model.py",
    )
    task = SingularityJSONConfiguredPythonTask(provided_command=command, script_path="sir_model.py")
    # Add Singularity as COMPS assets
    task.common_assets.add_assets(AssetCollection.from_id_file(f"../../singularity/definitions/{sif_name}.id"))

elif platform_type == 'ContainerPlatform':
    command = CommandLine("python3 Assets/sir_model.py")
    task = JSONConfiguredPythonTask(
        script_path="sir_model.py"
    )
else:
    print("TODO for Slurm and File/Process platfroms")
    print("Need to use python_analysis.sif image")
    exit(1)

# Set parameters
task.parameters = {
    "N": 10000,
    "beta": 0.5,
    "gamma": 0.1,
    "days": 160
}
ts = TemplatedSimulations(base_task=task)
# Create experiment
experiment = Experiment.from_task(
    task,
    name="SIR Python Model - Single Run"
)

# Run experiment
experiment.run(
    platform=platform,
    wait_until_done=True
)

print(f"Experiment ID: {experiment.id}")
print(f"Status: {experiment.status}")