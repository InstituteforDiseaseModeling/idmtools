"""
Here we implement the SlurmPlatform experiment operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from typing import TYPE_CHECKING
from dataclasses import dataclass
from idmtools_platform_file.platform_operations.json_metadata_operations import \
    JSONMetadataOperations as FileJSONMetadataOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmJSONMetadataOperations(FileJSONMetadataOperations):
    platform: 'SlurmPlatform'  # noqa: F821
