"""idmtools docker input/output operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import io
import json
import logging
import os
import shutil
import tarfile
import time
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from io import BytesIO
from logging import getLogger
from typing import BinaryIO, Dict, NoReturn, Optional, Union, Any
from docker.models.containers import Container
from idmtools import IdmConfigParser
from idmtools.core import TRUTHY_VALUES
from idmtools.core.system_information import get_data_directory
from idmtools.utils.decorators import ParallelizeDecorator
from idmtools_platform_local.infrastructure.postgres import PostgresContainer
from idmtools_platform_local.infrastructure.redis import RedisContainer
from idmtools_platform_local.infrastructure.workers import WorkersContainer

logger = getLogger(__name__)
# thread queue for docker copy operations
io_queue = ParallelizeDecorator()

# determine our default base directory. We almost always want to use the users home directory
# except odd environments like docker-in docker, special permissions, etc
SERVICES = [PostgresContainer, RedisContainer, WorkersContainer]


@dataclass
class DockerIO:
    """
    Provides most of our file operations for our docker containers/local platform.
    """
    host_data_directory: str = get_data_directory()
    _fileio_pool = ThreadPoolExecutor()

    def __post_init__(self):
        """
        Acts like our constructor after dataclasses has populated our fields.

        Currently we use it to initialize our docker client and get local system information
        """
        # Make sure the host_data_dir exists
        os.makedirs(self.host_data_directory, exist_ok=True)

        self.timeout = 1

    def delete_files_below_level(self, directory, target_level=1, current_level=1):
        """
        Delete files below a certain depth in a target directory.

        Args:
            directory: Target directory
            target_level: Depth to begin deleting. Default to 1
            current_level: Current level. We call recursively so this should be 1 on initial call.

        Returns:
            None

        Raises:
            PermissionError - Raised if there are issues deleting a file.
        """
        for fn in os.listdir(directory):
            file_path = os.path.join(directory, fn)
            try:
                # we only delete items at the target level
                if os.path.isfile(file_path) and target_level <= current_level:
                    logger.debug(f"Deleting {file_path}")
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    # if this is target level, let's delete it
                    if target_level <= current_level:
                        logger.debug(f"Deleting {file_path}")
                        shutil.rmtree(file_path)
                    else:
                        clevel = current_level + 1 if current_level >= 1 else 1
                        self.delete_files_below_level(file_path, target_level, clevel)
            except PermissionError as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.exception(e)
                pass

    def cleanup(self, delete_data: bool = True,
                shallow_delete: bool = os.getenv('SHALLOW_DELETE', '0').lower() in TRUTHY_VALUES) -> NoReturn:
        """
        Stops the running services, removes local data, and removes network.

        You can optionally disable the deleting of local data.

        Args:
            delete_data(bool): When true, deletes local data
            shallow_delete(bool): Deletes the data but not the container folders(redis, workers). Preferred to preserve
                permissions and resolve docker issues

        Returns:
            (NoReturn)
        """
        try:
            if delete_data and not shallow_delete:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Deleting local platform data at: {self.host_data_directory}")
                shutil.rmtree(self.host_data_directory, True)
            elif delete_data and shallow_delete:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"Shallow deleting: {self.host_data_directory}")
                self.delete_files_below_level(self.host_data_directory, 2)
        except PermissionError:
            print(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            logger.warning(f"Cannot cleanup directory {self.host_data_directory} because it is still in use")
            pass

    @io_queue.parallelize
    def copy_to_container(self, container: Container, destination_path: str,
                          file: Optional[Union[str, bytes]] = None,
                          content: Union[str, bytes] = None,
                          dest_name: Optional[str] = None) -> bool:
        """
        Copies a physical file or content in memory to a container.

        You can also choose a different name for the destination file by using the dest_name option.

        Args:
            container: Container to copy the file to
            file:  Path to the file to copy
            content: Content to copy
            destination_path: Path within the container to copy the file to(should be a directory)
            dest_name: Optional parameter for destination filename. By default, the source filename is used

        Returns:
            (bool) True if the copy succeeds, False otherwise
        """
        if content:
            if isinstance(content, dict):
                content = json.dumps(content)
            if isinstance(content, str):
                file = BytesIO(content.encode('utf-8'))
            else:
                file = content

        if file and isinstance(file, bytes):
            file = BytesIO(file)

        if type(file) is str:

            name = dest_name if dest_name else os.path.basename(file)
            if destination_path.startswith("/data"):
                destination_path = destination_path.replace('/data', '/workers')[1:]
            target_file = os.path.join(self.host_data_directory, destination_path, name)
            logger.debug(f'Copying {file} to docker container {container.id}:{target_file}')

            # Make sure to have the correct separators for the path
            target_file = target_file.replace('/', os.sep).replace('\\', os.sep)

            # Do the copy
            shutil.copy(file, target_file)
            return True
        elif isinstance(file, BytesIO):
            target_file = os.path.join(self.host_data_directory, destination_path.replace('/data', '/workers')[1:],
                                       dest_name)
            # Make sure to have the correct separators for the path
            target_file = target_file.replace('/', os.sep).replace('\\', os.sep)

            logger.debug(f'Copying {dest_name} to docker container {container.id}:{destination_path} '
                         f'through {target_file}')

            with open(target_file, 'wb') as of:
                of.write(file.getvalue())
            return True

    def sync_copy(self, futures):
        """
        Sync the copy operations queue in the io_queue.

        This allows us to take advantage of multi-threaded copying while also making it convenient to have sync points, such as
        uploading the assets in parallel but pausing just before sync point.

        Args:
            futures: Futures to wait on.

        Returns:
            Final results of copy operations.
        """
        if not isinstance(futures, list):
            futures = [futures]
        return io_queue.get_results(futures)

    def copy_multiple_to_container(self, container: Container, files: Dict[str, Dict[str, Any]], join_on_copy: bool = True):
        """
        Copy multiple items to a container.

        Args:
            container: Target container
            files: Files to copy in form target directory -> filename -> data
            join_on_copy: Should we join the threading on copy(treat as an atomic unit)

        Returns:
            True if copy succeeded, false otherwise
        """
        results = []
        if IdmConfigParser.is_progress_bar_disabled():
            prog_items = files.items()
        else:
            from tqdm import tqdm
            prog_items = tqdm(files.items(), desc="Copying Assets to Local Platform", unit='file')
        for dest_path, sub_files in prog_items:
            for fn in sub_files:
                results.append(self.copy_to_container(container, destination_path=dest_path, **fn))

        if join_on_copy:
            return all(io_queue.get_results(results))
        # If we don't join, we assume the copy succeeds for now. This really means somewhere else should be handling the
        # data join for this
        return True

    @staticmethod
    def create_archive_from_bytes(content: Union[bytes, BytesIO, BinaryIO], name: str) -> BytesIO:
        """
        Create a tar archive from bytes. Used to copy to docker.

        Args:
            content: Content to copy into tar
            name: Name for file in archive

        Returns:
            (BytesIO) Return bytesIO object
        """
        if type(content) is bytes:
            content = BytesIO(content)
        content.seek(0, io.SEEK_END)
        file_length = content.tell()
        content.seek(0)
        pw_tarstream = BytesIO()
        pw_tar = tarfile.TarFile(fileobj=pw_tarstream, mode='w')
        tarinfo = tarfile.TarInfo(name=name)
        tarinfo.size = file_length
        tarinfo.mtime = time.time()
        # tarinfo.mode = 0600
        pw_tar.addfile(tarinfo, content)
        pw_tar.close()
        pw_tarstream.seek(0)
        return pw_tarstream

    def create_directory(self, dir: str) -> bool:
        """
        Create a directory in a container.

        Args:
            dir: Path to directory to create

        Returns:
            (ExecResult) Result of the mkdir operation
        """
        path = os.path.join(self.host_data_directory, dir.replace('/data', '/workers')[1:])
        path.replace('/', os.sep).replace('\\', os.sep)
        os.makedirs(path, exist_ok=True)
        return True
