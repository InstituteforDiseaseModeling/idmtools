"""idmtools assetize output work item.

Notes:
    - TODO add example heres

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import warnings
from logging import getLogger
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

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass(repr=False)
class AssetizeOutput(FileFilterWorkItem):
    """
    AssetizeOutput allows creating assets from previously ran items in COMPS.

    Notes:
        - TODO link examples here.
    """
    # Dictionary of tags to apply to the results asset collection
    asset_tags: Dict[str, str] = field(default_factory=dict)
    #: The asset collection created by Assetize
    asset_collection: AssetCollection = field(default=None)

    def __post_init__(self, item_name: str, asset_collection_id: UUID, asset_files: FileList, user_files: FileList, command: str):
        """Constructor AssetizeOutput init."""
        self._ssmt_script = str(PurePath(__file__).parent.joinpath("assetize_ssmt_script.py"))
        super().__post_init__(item_name, asset_collection_id, asset_files, user_files, command)

    def _extra_command_args(self, command: str):
        """Add our tags to the command."""
        for name, value in self.asset_tags.items():
            command += f' --asset-tag "{name}={value}"'
        return command

    def _filter_workitem_pre_creation(self, platform):
        """
        Callback to allow for pre-creation calls.

        In our case, we check if tags exist. If no tags exists, we use our defalts ones.

        Args:
            platform: Platform we are creating on.

        Returns:
            None
        """
        super(AssetizeOutput, self)._filter_workitem_pre_creation(platform)
        if len(self.asset_tags) == 0:
            self.__generate_tags()

    def __generate_tags(self):
        """
        Add the defaults tags to the WorkItem.

        Returns:
            None
        """
        for experiment in self.related_experiments:
            self.asset_tags['AssetizedOutputfromFromExperiment'] = str(experiment.id)
        for simulation in self.related_simulations:
            self.asset_tags['AssetizedOutputfromFromSimulation'] = str(simulation.id)
        for work_item in self.related_work_items:
            self.asset_tags['AssetizedOutputfromFromWorkItem'] = str(work_item.id)
        for ac in self.related_asset_collections:
            self.asset_tags['AssetizedOutputfromAssetCollection'] = str(ac.id)

    def run(self, wait_until_done: bool = False, platform: 'IPlatform' = None, wait_on_done_progress: bool = True, **run_opts) -> Union[AssetCollection, None]:
        """
        Run the AssetizeOutput.

        Args:
            wait_until_done: Wait until Done will wait for the workitem to complete
            platform: Platform Object
            wait_on_done_progress: When set to true, a progress bar will be shown from the item
            **run_opts: Additional options to pass to Run on platform

        Returns:
            AssetCollection created if item succeeds
        """
        p = super()._check_for_platform_from_context(platform)
        if 'wait_on_done' in run_opts:
            warnings.warn("wait_on_done will be deprecated soon. Please use wait_until_done instead.", DeprecationWarning, 2)
            user_logger.warning("wait_on_done will be deprecated soon. Please use wait_until_done instead.")
        p.run_items(self, wait_on_done_progress=wait_on_done_progress, **run_opts)
        if wait_until_done or run_opts.get('wait_on_done', False):
            return self.wait(wait_on_done_progress=wait_on_done_progress, platform=p)

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None) -> Union[AssetCollection, None]:
        """
        Waits on Assetize Workitem to finish. This first waits on any dependent items to finish(Experiment/Simulation/WorkItems).

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
