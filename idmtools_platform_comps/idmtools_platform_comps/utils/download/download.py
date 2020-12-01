import os
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from pathlib import PurePath
from uuid import UUID
from COMPS.Data import WorkItem
from tqdm import tqdm
from idmtools.assets.file_list import FileList
from idmtools.core import EntityStatus
from idmtools.entities.iplatform import IPlatform
from idmtools_platform_comps.utils.file_filter_workitem import FileFilterWorkItem
from idmtools_platform_comps.utils.general import get_file_as_generator

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass(repr=False)
class DownloadWorkItem(FileFilterWorkItem):
    output_path: str = field(default_factory=os.getcwd)
    delete_after_download: bool = field(default=True)
    zip_name: str = field(default='output.zip')

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        self._ssmt_script = str(PurePath(__file__).parent.joinpath("download_ssmt.py"))
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files, command)

    def _extra_command_args(self, command: str):
        if self.zip_name != "output.zip":
            command += f" --zip-name {self.zip_name}"

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None) -> None:
        """
        Waits on Download WorkItem to finish. This first waits on any dependent items to finish(Experiment/Simulation/WorkItems)

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
        opts = dict(wait_on_done_progress=wait_on_done_progress, timeout=timeout, refresh_interval=refresh_interval, platform=p)
        self._wait_on_children(**opts)

        super().wait(**opts)
        if self.status == EntityStatus.SUCCEEDED and not self.dry_run:
            # Download our zip
            po: WorkItem = self.get_platform_object(platform=self.platform)
            oi = po.retrieve_output_file_info([self.zip_name])
            with tqdm(total=oi[0].length, unit='B', unit_scale=True, unit_divisor=1024) as pbar:
                with open(PurePath(self.output_path).joinpath(self.zip_name), 'wb') as zo:
                    for chunk in get_file_as_generator(oi[0]):
                        pbar.update(len(chunk))
                        zo.write(chunk)

            if self.delete_after_download:
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Deleting workitem")
                user_logger.debug(f'Deleting workitem {self.uid}')
                po.delete()
                self.uid = None
