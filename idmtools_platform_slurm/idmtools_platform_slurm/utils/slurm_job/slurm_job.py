"""
This is a SlurmPlatform utility.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import subprocess
import time
from os import PathLike
from pathlib import Path
from dataclasses import dataclass, field
from typing import NoReturn, Union, List, TYPE_CHECKING
from idmtools.core import NoPlatformException
from jinja2 import Template
from logging import getLogger
from idmtools_platform_slurm.utils.slurm_job import create_slurm_indicator, slurm_installed
from typing import Tuple


user_logger = getLogger('user')

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

DEFAULT_TEMPLATE_FILE = "script_sbatch.sh.jinja2"
MSG = """Note: any output information from your script is stored in file stdout.txt under the script folder. For example, if you are running a script under current directory which kicks out another Slurm job, then the second Slurm job id is stored in stdout.txt under the current directory."""

TEMP_FILES = ['sbatch.sh', 'job_id.txt', 'job_status.txt', 'stdout.txt', 'stderr.txt']


def generate_script(platform: 'SlurmPlatform', command: str,
                    template: Union[Path, str] = DEFAULT_TEMPLATE_FILE, batch_dir: str = None, **kwargs) -> None:
    """
    Generate batch file sbatch.sh
    Args:
        platform: Slurm Platform
        command: execution command
        template: template to be used to build batch file
        kwargs: keyword arguments used to expand functionality
    Returns:
        None
    """
    from idmtools_platform_slurm.slurm_platform import CONFIG_PARAMETERS
    template_vars = dict(
        platform=platform,
        command=command
    )
    # Populate from our platform config vars
    for p in CONFIG_PARAMETERS:
        if getattr(platform, p) is not None:
            template_vars[p] = getattr(platform, p)

    template_vars.update(kwargs)

    if platform.modules:
        template_vars['modules'] = platform.modules

    with open(Path(__file__).parent.joinpath(template)) as tin:
        t = Template(tin.read())

    # Write our file
    if batch_dir is None:
        output_target = Path.cwd().joinpath("sbatch.sh")
    else:
        output_target = Path(batch_dir).joinpath("sbatch.sh")

    with open(output_target, "w") as tout:
        tout.write(t.render(template_vars))

    # Make executable
    platform._op_client.update_script_mode(output_target)


def check_file_and_job_id(file_path, timeout: int = 300, interval: int = 5) -> Tuple[bool, str]:
    """
    Wait for a file to be created and check if slurm job id exists in the file.

    Args:
        file_path (str): Path to the file to check.
        timeout (int): Maximum time (in seconds) to wait for the file and line.
        interval (int): Time interval (in seconds) between checks.

    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if the file exists and contains a valid job ID, False otherwise.
            - str: The job ID if found, otherwise an empty string.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        if os.path.exists(file_path):
            user_logger.info(f"File {file_path} found.")
            with open(file_path, 'r') as file:
                for line in file:
                    if 'Slurm Job Ids (' in line:
                        slurm_job_id = file.readline().strip()
                        if slurm_job_id.isdigit():
                            return True, slurm_job_id
            user_logger.warning(f"Not found slurm job id in {file_path}.")
        else:
            user_logger.info(f"File {file_path} not found yet. Waiting...")

        time.sleep(interval)

    user_logger.error(f"Timeout reached. File {file_path} or slurm job id not found.")
    return False, None



@dataclass(repr=False)
class SlurmJob:
    script_path: PathLike = field(init=True)
    platform: 'SlurmPlatform' = field(default=None, init=True)
    executable: str = field(default='python3', init=True)
    script_params: List[str] = field(default=None, init=True)
    cleanup: bool = field(default=True, init=True)

    def __post_init__(self):
        if self.script_path is None:
            raise RuntimeError("script_path is missing!")
        # load platform from context or from passed in value
        self.platform = self.__check_for_platform_from_context(self.platform)
        self.working_directory = Path(self.script_path).parent
        self.script_params = self.script_params if self.script_params is not None and len(
            self.script_params) > 0 else None
        self.slurm_job_id = None

    def initialization(self):
        # make str list so that we may join them together
        if self.script_params is not None:
            self.script_params = [str(i) for i in self.script_params]

        if self.script_params is not None:
            command = f"{self.executable} {Path(self.script_path).name} {' '.join(self.script_params)}"
        else:
            command = f"{self.executable} {Path(self.script_path).name}"

        generate_script(self.platform, command, batch_dir=self.working_directory)


    def run(self, dry_run: bool = False, **kwargs) -> NoReturn:
        if self.cleanup:
            self.clean(self.working_directory)

        self.initialization()

        if not dry_run:
            if not slurm_installed():
                user_logger.warning('Slurm is not installed/available!')
                exit(-1)

            user_logger.info('Script is running as a slurm job!\n')
            create_slurm_indicator()
            result = subprocess.run(['sbatch', '--parsable', 'sbatch.sh'], stdout=subprocess.PIPE,
                            cwd=str(self.working_directory))
            self.slurm_job_id = result.stdout.decode('utf-8').strip().split(';')[0]

            user_logger.info(f"{'job_id: '.ljust(20)} {self.slurm_job_id}")
            user_logger.info(f"{'job_directory: '.ljust(20)} {self.platform.job_directory}\n")

            # Check if stdout.txt is created and job id exists in there
            stdout_file = os.path.join(self.working_directory, 'stdout.txt')
            is_exists, slurm_job_id = check_file_and_job_id(stdout_file)
            if is_exists and slurm_job_id is not None:
                # print stdout.txt on console
                with open(stdout_file, "r") as f:
                    read_data = f.read()
                    user_logger.info(read_data)
                user_logger.info("To check job status, run command:")
                user_logger.info(f"scontrol show job {slurm_job_id}")
                user_logger.info(f"sacct -j {slurm_job_id} --format=JobID,State,Start,End")
            else:
                user_logger.warning("Check status.txt for job details.")
                user_logger.warning(MSG)
        else:
            user_logger.warning('Script is runing with dry_run = True')

    def __check_for_platform_from_context(self, platform) -> 'IPlatform':  # noqa: F821
        """
        Try to determine platform of current object from self or current platform.

        Args:
            platform: Passed in platform object

        Raises:
            NoPlatformException: when no platform is on current context
        Returns:
            Platform object
        """
        if self.platform is None:
            # check context for current platform
            if platform is None:
                from idmtools.core.context import CURRENT_PLATFORM
                if CURRENT_PLATFORM is None:
                    raise NoPlatformException("No Platform defined on object, in current context, or passed to run")
                platform = CURRENT_PLATFORM
            self.platform = platform
        return self.platform

    def clean(self, cwd: str = os.getcwd()):
        """
        Delete generated slurm job related files.
        Args:
            cwd: the directory containing the files
        Returns:
            None
        """
        for file_path in TEMP_FILES:
            f = os.path.join(cwd, file_path)
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass
