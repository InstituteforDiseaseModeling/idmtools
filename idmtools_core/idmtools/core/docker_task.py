"""
DockerTask provides a utility to run docker images.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional, Type
from idmtools import __version__ as idmtools_version, IdmConfigParser
from idmtools.assets import AssetCollection, json
from idmtools.core.logging import getLogger
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class DockerTask(ITask):
    """
    Provides a task to run or optionally build a docker container.
    """
    image_name: str = field(default=None, metadata={"md": True})
    # Optional config to build the docker image
    build: bool = field(default=False, metadata={"md": True})
    build_path: Optional[str] = field(default=None, metadata={"md": True})
    # This should in the build_path directory
    Dockerfile: Optional[str] = field(default=None, metadata={"md": True})
    pull_before_build: bool = field(default=True, metadata={"md": True})
    use_nvidia_run: bool = field(default=False, metadata={"md": True})

    __image_built: bool = field(default=False)

    def __post_init__(self):
        """
        Set our platform requirements and optionally trigger image build.

        Returns:
            None
        """
        super().__post_init__()
        self.add_platform_requirement(PlatformRequirements.DOCKER)
        if self.build:
            self.build_image()

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather common(experiment-level) assets from task.

        Returns:
            AssetCollection containing all the common assets
        """
        if self.image_name is None:
            raise ValueError("Image Name is required")
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient(simulation-level) assets from task.

        Returns:
            AssetCollection
        """
        return self.transient_assets

    def build_image(self, spinner=None, **extra_build_args):
        """
        Build our docker image.

        Args:
            spinner: Should we display a CLI spinner
            **extra_build_args: Extra build arguments to pass to docker

        Returns:
            None
        """
        if not self.__image_built:
            import docker
            from docker.errors import BuildError
            if spinner:
                spinner.text = f"Building {self.image_name}"
            # if the build_path is none use current working directory
            if self.build_path is None:
                self.build_path = os.getcwd()

            client = docker.client.from_env()
            build_config = dict(
                path=self.build_path,
                dockerfile=self.Dockerfile,
                tag=self.image_name,
                labels=dict(
                    uildstamp=f'built-by idmtools {idmtools_version}',
                    builddate=str(datetime.now(timezone(timedelta(hours=-8)))))
            )
            if extra_build_args:
                build_config.update(extra_build_args)
            logger.debug(f"Build configuration used: {str(build_config)}")
            self.__image_built = True
            if not IdmConfigParser.is_progress_bar_disabled():
                from tqdm import tqdm
                prog = tqdm(
                    desc='Building docker image',
                    total=10,
                    bar_format='Building Docker Image: |{bar}| {percentage:3.0f}% [{n_fmt}/{total_fmt}] [{elapsed}] {desc}'
                )
            try:
                build_step = None
                # regular expression to grab progress
                progress_grep = re.compile(r'Step ([0-9]+)/([0-9]+) : (.*)')
                # regular expression to filter out ansi codes
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                for line in client.api.build(**build_config):
                    line = json.loads(line)
                    if 'stream' in line:
                        line = line['stream']
                        line = ansi_escape.sub('', line).strip()
                        # strip unicode data
                        line = "".join(ch for ch in line if unicodedata.category(ch)[0] != "C")
                        logger.debug('Raw Docker Output: %s', line)
                        if line:
                            grps = progress_grep.match(line)
                            if grps:
                                try:
                                    step = int(grps.group(1))
                                    total_steps = int(grps.group(2))
                                    if prog:
                                        prog.n = step
                                        prog.total = total_steps
                                    line = grps.group(3)
                                except:  # noqa E722
                                    pass
                                if prog:
                                    prog.set_description(line)
                                build_step = line
                            # update build step with output
                            elif build_step:
                                if len(line) > 40:
                                    line = line[:40]
                                if prog:
                                    prog.set_description(f'{build_step}: {line}')
                    elif 'status' in line:
                        line = line['status'].strip()
                        if prog:
                            prog.set_description(line)

                logger.info('Build Successful)')
            except BuildError as e:
                logger.info(f"Build failed for {self.image_name} with message {e.msg}")
                logger.info(f'Build log: {e.build_log}')
                sys.exit(-1)
            finally:
                if prog:
                    prog.close()

    def reload_from_simulation(self, simulation: 'Simulation'):  # noqa E821
        """
        Method to reload task details from simulation object. Currently we do not do this for docker task.

        Args:
            simulation: Simulation to load data from

        Returns:
            None
        """
        pass


class DockerTaskSpecification(TaskSpecification):
    """
    DockerTaskSpecification provides the task plugin to idmtools for DockerTask.
    """

    def get(self, configuration: dict) -> DockerTask:
        """
        Get instance of DockerTask with configuration provided.

        Args:
            configuration: configuration for DockerTask

        Returns:
            DockerTask with configuration
        """
        return DockerTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin.

        Returns:
            Plugin description
        """
        return "Defines a docker command"

    def get_type(self) -> Type[DockerTask]:
        """
        Get type of task provided by plugin.

        Returns:
            DockerTask
        """
        return DockerTask
