import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

from tqdm import tqdm

from idmtools import __version__ as idmtools_version
from idmtools.assets import AssetCollection, json
from idmtools.core.logging import getLogger
from idmtools.entities.itask import ITask
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class DockerTask(ITask):
    image_name: str = None
    # Optional config to build the docker image
    build: bool = False
    build_path: Optional[str] = None
    # This should in the build_path directory
    Dockerfile: Optional[str] = None
    pull_before_build: bool = True
    use_nvidia_run: bool = False

    __image_built: bool = False

    def __post_init__(self):
        super().__post_init__()
        self.add_platform_requirement(PlatformRequirements.DOCKER)
        if self.build:
            self.build_image()

    def gather_common_assets(self) -> AssetCollection:
        if self.image_name is None:
            raise ValueError("Image Name is required")
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        return self.transient_assets

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
                                    prog.n = step
                                    prog.total = total_steps
                                    line = grps.group(3)
                                except:  # noqa E722
                                    pass
                                prog.set_description(line)
                                build_step = line
                            # update build step with output
                            elif build_step:

                                if len(line) > 40:
                                    line = line[:40]
                                prog.set_description(f'{build_step}: {line}')
                    elif 'status' in line:
                        line = line['status'].strip()
                        prog.set_description(line)

                logger.info('Build Successful)')
            except BuildError as e:
                logger.info(f"Build failed for {self.image_name} with message {e.msg}")
                logger.info(f'Build log: {e.build_log}')
                sys.exit(-1)
            finally:
                prog.close()

    def reload_from_simulation(self, simulation: 'Simulation'):  # noqa E821
        pass


class DockerTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> DockerTask:
        return DockerTask(**configuration)

    def get_description(self) -> str:
        return "Defines a docker command"
