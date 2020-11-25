import os
import shutil
from dataclasses import field, dataclass
from logging import getLogger, DEBUG
from threading import Lock
from pathlib import PurePath
from typing import Any, Type, Union
from uuid import UUID
from zipfile import ZipFile
from idmtools.assets import AssetCollection
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_asset_collection_operations import IPlatformAssetCollectionOperations
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation

logger = getLogger(__name__)


# Class to distinguish between regular AC and our platform and for type mapping on the platform
class FilePlatformAssetCollection(AssetCollection):
    pass


@dataclass
class FilePlatformAssetCollectionOperations(IPlatformAssetCollectionOperations):
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=FilePlatformAssetCollection)

    def platform_create(self, asset_collection: AssetCollection, parent: Union[Experiment, Simulation, IWorkflowItem], **kwargs) -> Any:
        if isinstance(parent, (Experiment, IWorkflowItem)):
            base_directory = parent._metadata['output_directory']
            is_common = asset_collection == parent.assets
            use_links = parent._metadata.get('use_links', False) or self.platform.use_links
            archive = parent._metadata.get('archive', None)
        elif isinstance(parent, Simulation):
            base_directory = parent._metadata['output_directory'] if 'output_directory' in parent._metadata else parent.parent._metadata['output_directory']
            is_common = asset_collection == parent.task.transient_assets
            use_links = parent.parent._metadata.get('use_links', False) or self.platform.use_links
            archive = parent.parent._metadata.get('archive', None)
        else:
            raise ValueError("You must provide a parent of the assets that is a Experiment, Simulation, or a WorkItem")

        base_directory = PurePath(base_directory)
        if is_common:
            base_directory = base_directory.joinpath("Assets")

        if archive and isinstance(parent, Simulation):
            from idmtools_platform_file._api.experiment_operations import EXPERIMENT_LOCKS
            sn = parent._metadata['sn']
            l: Lock = EXPERIMENT_LOCKS[parent.parent.uid]
            for file in asset_collection:
                l.acquire()
                rf = PurePath(sn).joinpath(file.short_remote_path())
                if file.absolute_path:
                    archive.write(file.absolute_path, str(rf))
                else:
                    with archive.open(str(rf), 'w') as of:
                        of.write(file.bytes)
                l.release()
        else:
            if not os.path.exists(base_directory):
                if logger.isEnabledFor(DEBUG):
                    logger.debug("Creating output directory for Assets")
                os.makedirs(base_directory, exist_ok=True)

            for file in asset_collection:
                fn = base_directory.joinpath(file.short_remote_path())
                if file.absolute_path:
                    if use_links:
                        os.symlink(file.absolute_path, fn)
                    else:
                        shutil.copy(file.absolute_path, fn)
                else:
                    with open(fn, 'wb') as fout:
                        fout.write(file.bytes)

    def get(self, asset_collection_id: UUID, **kwargs) -> Any:
        pass
