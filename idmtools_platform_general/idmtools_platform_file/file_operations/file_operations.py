"""
Here we implement the operations_interface.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import os
import shlex
import shutil
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Union
from idmtools.core import ItemType, EntityStatus
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools_platform_file.assets import generate_script, generate_simulation_script
from idmtools_platform_file.file_operations.operations_interface import IOperations
from idmtools_platform_file.platform_operations.utils import FILE_MAPS, validate_file_path_length, \
    clean_item_name, validate_folder_files_path_length, FileExperiment, FileSimulation, FileSuite
from idmtools.utils.decorators import check_symlink_capabilities

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class FileOperations(IOperations):
    """
    Implement operations_interface.
    """

    def entity_display_name(self, item: Union[Suite, Experiment, Simulation]) -> str:
        """
        Get display name for entity.
        Args:
            item: Suite, Experiment or Simulation
        Returns:
            str
        """
        use_name = getattr(self.platform, "name_directory", False)
        use_sim_name = getattr(self.platform, "sim_name_directory", True)

        # Determine if we should include name
        if isinstance(item, Simulation) and not use_sim_name:
            use_name = False

        if use_name and getattr(item, "name", None):
            safe_name = clean_item_name(item.name)
            return f"{safe_name}_{item.id}"
        else:
            return item.id

    def get_directory(self, item: Union[Suite, Experiment, Simulation]) -> Path:
        """
        Get item's path.
        Args:
            item: Suite, Experiment, Simulation
        Returns:
            item file directory
        """
        job_dir = Path(self.platform.job_directory)
        if isinstance(item, (FileSimulation, FileExperiment, FileSuite)):
            item_dir = item.get_directory()
        elif isinstance(item, Suite):
            return job_dir / f"s_{self.entity_display_name(item)}"
        elif isinstance(item, Experiment):
            suite_id = item.parent_id or item.suite_id
            suite = None

            # Try to retrieve suite from platform or parent
            if suite_id:
                suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)  # raw is True to get FileSuite object

            if suite:
                suite_dir = job_dir / f"s_{self.entity_display_name(suite)}"
                return suite_dir / f"e_{self.entity_display_name(item)}"
            else:
                return job_dir / f"e_{self.entity_display_name(item)}"
        elif isinstance(item, Simulation):
            exp = item.parent
            if exp is None:
                raise RuntimeError("Simulation missing parent!")
            exp_dir = self.get_directory(exp)
            return exp_dir / self.entity_display_name(item)
        else:
            raise RuntimeError(f"Get directory is not supported for {type(item)} object on FilePlatform")

        return item_dir

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        """
        Get item's path by id.
        Args:
            item_id: entity id (Suite, Experiment, Simulation)
            item_type: the type of items (Suite, Experiment, Simulation)
        Returns:
            item file directory
        """
        metas = self.platform._metas.filter(item_type=item_type, property_filter={'id': str(item_id)})
        if len(metas) > 0:
            return Path(metas[0]['dir'])
        else:
            raise RuntimeError(f"Not found path for item_id: {item_id} with type: {item_type}.")

    def mk_directory(self, item: Union[Suite, Experiment, Simulation] = None, dest: Union[Path, str] = None,
                     exist_ok: bool = True) -> None:
        """
        Make a new directory.
        Args:
            item: Suite/Experiment/Simulation
            dest: the folder path
            exist_ok: True/False
        Returns:
            None
        """
        if dest is not None:
            target = Path(dest)
        elif isinstance(item, (Suite, Experiment, Simulation)):
            target = self.get_directory(item)
        else:
            raise RuntimeError('Only support Suite/Experiment/Simulation or not None dest.')

        # Validate target path length
        validate_file_path_length(self.platform.job_directory)
        target.mkdir(parents=True, exist_ok=exist_ok)

    @check_symlink_capabilities
    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link files.
        Args:
            target: the source file path
            link: the file path
        Returns:
            None
        """
        target = Path(target).absolute()
        link = Path(link).absolute()
        if self.platform.sym_link:
            # Ensure the source folder exists
            if not target.exists():
                raise FileNotFoundError(f"Source folder does not exist: {target}")

            # Compute the relative path from the destination to the source
            relative_source = os.path.relpath(target, link.parent)

            # Remove existing symbolic link or file at destination if it exists
            if link.exists() or link.is_symlink():
                link.unlink()

            # Create the symbolic link
            try:
                link.symlink_to(relative_source, target_is_directory=False)
            except OSError as e:
                user_logger.error(f"\n Failed to create symbolic link: {e}")
                if self.platform.system() == 'Windows':
                    user_logger.warning("\n/!\\ WARNING:  Please follow the instructions to enable Developer Mode for Windows: ")
                    user_logger.warning("https://learn.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development. \n")
                exit(-1)
        else:
            shutil.copyfile(target, link)

    @check_symlink_capabilities
    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link directory/files.
        Args:
            target: the source folder path
            link: the folder path
        Returns:
            None
        """
        target = Path(target).absolute()
        link = Path(link).absolute()

        # Validate file path length
        validate_folder_files_path_length(target, link)

        if self.platform.sym_link:
            # Ensure the source folder exists
            if not target.exists():
                raise FileNotFoundError(f"Source folder does not exist: {target}")

            # Compute the relative path from the destination to the source
            relative_source = os.path.relpath(target, link.parent)

            # Remove existing symbolic link or folder at destination if it exists
            if link.exists() or link.is_symlink():
                if link.is_symlink():
                    link.unlink()
                else:
                    shutil.rmtree(link)

            # Create the symbolic link
            try:
                link.symlink_to(relative_source, target_is_directory=True)
            except OSError as e:
                user_logger.error(f"\n Failed to create symbolic link: {e}")
                if self.platform.system() == 'Windows':
                    user_logger.warning("\n/!\\ WARNING:  Please follow the instructions to enable Developer Mode for Windows: ")
                    user_logger.warning("https://learn.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development. \n")
                exit(-1)
        else:
            shutil.copytree(target, link, dirs_exist_ok=True)

    @staticmethod
    def update_script_mode(script_path: Union[Path, str], mode: int = 0o777) -> None:
        """
        Change file mode.
        Args:
            script_path: script path
            mode: permission mode
        Returns:
            None
        """
        script_path = Path(script_path)
        script_path.chmod(mode)

    def make_command_executable(self, simulation: Simulation) -> None:
        """
        Make simulation command executable.
        Args:
            simulation: idmtools Simulation
        Returns:
            None
        """
        exe = simulation.task.command.executable
        if exe == 'singularity':
            # split the command
            cmd = shlex.split(simulation.task.command.cmd.replace("\\", "/"))
            # get real executable
            exe = cmd[3]

        sim_dir = self.get_directory(simulation)
        exe_path = sim_dir.joinpath(exe)

        # see if it is a file
        if exe_path.exists():
            exe = exe_path
        elif shutil.which(exe) is not None:
            exe = Path(shutil.which(exe))
        else:
            logger.debug(f"Failed to find executable: {exe}")
            exe = None
        try:
            if exe and not os.access(exe, os.X_OK):
                self.update_script_mode(exe)
        except:
            logger.debug(f"Failed to change file mode for executable: {exe}")

    def get_simulation_status(self, sim_id: str, **kwargs) -> EntityStatus:
        """
        Retrieve simulation status.
        Args:
            sim_id: Simulation ID
            kwargs: keyword arguments used to expand functionality
        Returns:
            EntityStatus
        """
        sim_dir = self.get_directory_by_id(sim_id, ItemType.SIMULATION)

        # Check process status
        job_status_path = sim_dir.joinpath('job_status.txt')
        if job_status_path.exists():
            status = open(job_status_path).read().strip()
            if status in ['100', '0', '-1']:
                status = FILE_MAPS[status]
            else:
                status = FILE_MAPS['100']  # To be safe
        else:
            status = FILE_MAPS['None']

        return status

    def create_file(self, file_path: str, content: str) -> None:
        """
        Create a file with given content and file path.

        Args:
            file_path: the full path of the file to be created
            content: file content
        Returns:
            Nothing
        """
        with open(file_path, 'w') as f:
            f.write(content)

    def create_batch_file(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        if isinstance(item, Experiment):
            generate_script(self.platform, item, **kwargs)
        elif isinstance(item, Simulation):
            generate_simulation_script(self.platform, item, **kwargs)
        else:
            raise NotImplementedError(f"{item.__class__.__name__} is not supported for batch creation.")
