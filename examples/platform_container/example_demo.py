from idmtools.entities.command_task import CommandTask
from idmtools.entities.experiment import Experiment
from idmtools_platform_container.container_platform import ContainerPlatform

# Initialize the platform
from idmtools.core.platform_factory import Platform
platform = Platform('Container', job_directory="destination_directory")
# OR
# platform = ContainerPlatform(job_directory="destination_directory")

# Define task
command = "echo 'Hello, World!'"
task = CommandTask(command=command)
# Run an experiment
experiment = Experiment.from_task(task, name="example")
experiment.run(platform=platform)