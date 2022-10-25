"""idmtools download work item output.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import sys
import warnings
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from logging import getLogger, DEBUG
from pathlib import PurePath
from uuid import UUID
from COMPS.Data import WorkItem
from tqdm import tqdm

from idmtools import IdmConfigParser
from idmtools.assets.file_list import FileList
from idmtools.core import EntityStatus
from idmtools.entities.iplatform import IPlatform
from idmtools_platform_comps.utils.file_filter_workitem import FileFilterWorkItem
from idmtools_platform_comps.utils.general import get_file_as_generator

logger = getLogger(__name__)
user_logger = getLogger('user')


class CompressType(Enum):
    """Defines the compression types we support.

    lzma is the best balance between speed and compression ratio typically
    """
    lzma = 'lzma'
    deflate = 'deflate'
    bz = "bz"


@dataclass(repr=False)
class DownloadWorkItem(FileFilterWorkItem):
    """
    DownloadWorkItem provides a utility to download items through a workitem with compression.

    The main advantage of this over Analyzers is the compression. This is most effective when the targets to download have many
    items that are similar to download. For example, an experiment with 1000 simulations with similar output can greatly benefit
    from downloading through this method.

    Notes:
        - TODO Link examples here.
    """
    output_path: str = field(default_factory=os.getcwd)
    extract_after_download: bool = field(default=True)
    delete_after_download: bool = field(default=True)
    zip_name: str = field(default='output.zip')
    compress_type: CompressType = field(default=None)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList,
                      command: str):
        """
        Constructor for DownloadWorkItem.

        Args:
            item_name: item name
            asset_collection_id: AssetCollection id
            asset_files: Asset files
            user_files: user asset files
            command: command

        Returns:
            None
        """
        self._ssmt_script = str(PurePath(__file__).parent.joinpath("download_ssmt.py"))
        if self.compress_type is None:
            if (self.extract_after_download and self.delete_after_download) or sys.platform != 'win32':
                self.compress_type = CompressType.lzma
            elif sys.platform == 'win32':
                self.compress_type = CompressType.deflate
            else:
                self.compress_type = CompressType.lzma
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files, command)
        warnings.warn(
            message="DownloadWorkItem is deprecated. Until a replacement is added, please use native COMPS scripts. See "
                    "'https://github.com/InstituteforDiseaseModeling/pyCOMPS/blob/master/examples/retrieve_simulation_outputs_for_experiment.py'",
            category=FutureWarning)

    def _extra_command_args(self, command: str) -> str:
        """
        Add specific additional arguments for the download command. In this case, only the zip name and compression type can be changed.

        Args:
            command: Command to append additional items to

        Returns:
            Updated command
        """
        if self.zip_name != "output.zip":
            command += f" --zip-name {self.zip_name}"
        if self.compress_type != "lzma":
            command += f" --compress-type {self.compress_type.value}"
        return command

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None,
             platform: 'IPlatform' = None) -> None:
        """
        Waits on Download WorkItem to finish. This first waits on any dependent items to finish(Experiment/Simulation/WorkItems).

        Args:
            wait_on_done_progress: When set to true, a progress bar will be shown from the item
            timeout: Timeout for waiting on item. If none, wait will be forever
            refresh_interval: How often to refresh progress
            platform: Platform

        Returns:
            AssetCollection created if item succeeds
        """
        # wait on related items before we wait on our item
        p = super()._check_for_platform_from_context(platform)
        opts = dict(wait_on_done_progress=wait_on_done_progress, timeout=timeout, refresh_interval=refresh_interval,
                    platform=p)
        self._wait_on_children(**opts)

        super().wait(**opts)
        if self.status == EntityStatus.SUCCEEDED and not self.dry_run:
            # Download our zip
            po: WorkItem = self.get_platform_object(platform=self.platform)
            if self._uid:
                oi = po.retrieve_output_file_info([self.zip_name])
                zip_name = PurePath(self.output_path).joinpath(self.zip_name)
                with tqdm(total=oi[0].length, unit='B', unit_scale=True, unit_divisor=1024,
                          desc="Downloading Files") as pbar:
                    self.__download_file(oi, pbar, zip_name)
                    if self.extract_after_download:
                        self.__extract_output(zip_name)

                if self.delete_after_download:
                    if self.extract_after_download:
                        if IdmConfigParser.is_output_enabled():
                            user_logger.debug(f"Removing {zip_name}")
                        os.remove(zip_name)
                    if IdmConfigParser.is_output_enabled():
                        user_logger.debug(f'Deleting workitem {self.uid}')
                    po.delete()
                    self.uid = None

    def __extract_output(self, zip_name):
        """
        Extra output from our zip file.

        Args:
            zip_name: Zip file to extract

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Extracting {zip_name}")
        with zipfile.ZipFile(zip_name, 'r') as zin:
            zin.extractall(self.output_path)

    def __download_file(self, oi, pbar, zip_name):
        """
        Download our file tracking progress as we go.

        Args:
            oi: Stream to download
            pbar: Prograss Bar
            zip_name: Zip file to save to

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Downloading file to {zip_name}")
        parent_dir = PurePath(zip_name).parent
        os.makedirs(parent_dir, exist_ok=True)
        with open(zip_name, 'wb') as zo:
            for chunk in get_file_as_generator(oi[0]):
                pbar.update(len(chunk))
                zo.write(chunk)
