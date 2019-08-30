from dataclasses import dataclass, field
import os
from idmtools.entities import CommandLine
from idmtools_models.python import PythonExperiment, PythonSimulation


@dataclass(repr=False)
class DockerizedPythonExperiment(PythonExperiment):
    """
    Dockerized Python Experiment. Currently planned for Comps/Local platform
    """
    docker_image: str = field(default=None)
    # extra_volume_mounts: str = field(default=None)

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=PythonSimulation)
        if self.docker_image is None:
            raise ValueError("Docker image is required when running a dockerized python simulation")

    def pre_creation(self):
        super().pre_creation()

        # Create the command line according to the location of the model
        # the data path will be updated by the platform
        self.command = CommandLine("docker", "run", "-v", "{data_path}:/workdir", f"{self.docker_image}", "python",
                                   f"./Assets/{os.path.basename(self.model_path)}", "config.json")
        raise NotImplementedError("This feature is still in progress")
