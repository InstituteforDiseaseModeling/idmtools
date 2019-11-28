import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from logging import getLogger
from typing import Set, Optional, NoReturn
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools import __version__ as idmtools_version
from idmtools.registry.task_specification import TaskSpecification
from idmtools.utils.decorators import optional_yaspin_load

logger = getLogger(__name__)


@dataclass
class DockerTask(ITask):

    image_name: str = None
    # Optional config to build the docker image
    build: bool = False
    build_path: Optional[str] = None
    # This should in the build_path directory
    Dockerfile: Optional[str] = None
    pull_before_build: bool = True

    __image_built: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.add_platform_requirement(PlatformRequirements.DOCKER)
        if self.build:
            self.build_image()

    def gather_assets(self) -> NoReturn:
        if self.image_name is None:
            raise ValueError("Image Name is required")

    @optional_yaspin_load(text="Building docker image")
    def build_image(self, spinner=None, **extra_build_args):
        if not self.__image_built:
            import docker
            from docker.errors import BuildError
            if spinner:
                spinner.text = f"Building {self.image_name}"
            # if the build_path is none use current working directory
            if self.build_path is None:
                self.build_path = os.getcwd()

            client = docker.client.from_env()
            build_config = dict(path=self.build_path, dockerfile=self.Dockerfile, tag=self.image_name,
                                labels=dict(
                                    buildstamp=f'built-by idmtools {idmtools_version}',
                                    builddate=str(datetime.now(timezone(timedelta(hours=-8)))))
                                )
            if extra_build_args:
                build_config.update(extra_build_args)
            logger.debug(f"Build configuration used: {str(build_config)}")
            self.__image_built = True
            try:
                result = client.images.build(**build_config)
                logger.info(f'Build Successful of {result[0].tag} ({result[0].id})')
            except BuildError as e:
                logger.info(f"Build failed for {self.image_name} with message {e.msg}")
                logger.info(f'Build log: {e.build_log}')
                sys.exit(-1)

    def reload_from_simulation(self, simulation: 'Simulation'):
        pass


class DockerTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> DockerTask:
        return DockerTask(**configuration)

    def get_description(self) -> str:
        return "Defines a docker command"
