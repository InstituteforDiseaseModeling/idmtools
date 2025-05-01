"""
Here we implement the SlurmPlatform asset collection operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass
from logging import getLogger
from typing import TYPE_CHECKING
from idmtools_platform_file.platform_operations.asset_collection_operations import FilePlatformAssetCollectionOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

logger = getLogger(__name__)
user_logger = getLogger("user")

EXCLUDE_FILES = ['_run.sh', 'metadata.json', 'stdout.txt', 'stderr.txt', 'status.txt', 'job_id.txt', 'job_status.txt']


@dataclass
class SlurmPlatformAssetCollectionOperations(FilePlatformAssetCollectionOperations):
    """
    Provides AssetCollection Operations to SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
