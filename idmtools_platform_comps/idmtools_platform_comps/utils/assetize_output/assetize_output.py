from pathlib import PurePath
from uuid import UUID
from dataclasses import dataclass, field
from typing import Union, Dict
from idmtools.assets import AssetCollection
from idmtools.assets.file_list import FileList
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.relation_type import RelationType
from idmtools.core.enums import EntityStatus
from idmtools_platform_comps.utils.file_filter_workitem import FileFilterWorkItem


@dataclass(repr=False)
class AssetizeOutput(FileFilterWorkItem):
    # Dictionary of tags to apply to the results asset collection
    asset_tags: Dict[str, str] = field(default_factory=dict)
    #: The asset collection created by Assetize
    asset_collection: AssetCollection = field(default=None)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        self._ssmt_script = str(PurePath(__file__).parent.joinpath("assetize_ssmt_script.py"))
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files, command)

    def _extra_command_args(self, command: str):
        for name, value in self.asset_tags.items():
            command += f' --asset-tag "{name}={value}"'
        return command

    def run(self, wait_until_done: bool = False, platform: 'IPlatform' = None, wait_on_done_progress: bool = True, wait_on_done: bool = True, **run_opts) -> Union[AssetCollection, None]:
        """
        Run the AssetizeOutput

        Args:
            wait_until_done: Wait until Done will wait for the workitem to complet
            platform: Platform Object
            wait_on_done_progress: When set to true, a progress bar will be shown from the item
            wait_on_done: Wait for item to be done. This will first wait on any dependencies
            **run_opts: Additional options to pass to Run on platform

        Returns:
            AssetCollection created if item succeeds
        """
        p = super()._check_for_platform_from_context(platform)
        p.run_items(self, wait_on_done_progress=wait_on_done_progress, **run_opts)
        if wait_until_done or wait_on_done:
            return self.wait(wait_on_done_progress=wait_on_done_progress, platform=p)

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None) -> Union[AssetCollection, None]:
        """
        Waits on Assetize Workitem to finish. This first waits on any dependent items to finish(Experiment/Simulation/WorkItems)

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
            # If we succeeded, get our AC
            comps_workitem = self.get_platform_object(force=True)
            acs = comps_workitem.get_related_asset_collections(RelationType.Created)
            if acs:
                self.asset_collection = AssetCollection.from_id(acs[0].id, platform=p)
                return self.asset_collection
