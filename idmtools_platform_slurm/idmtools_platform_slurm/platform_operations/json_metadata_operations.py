from typing import TYPE_CHECKING, Type
from dataclasses import dataclass, field
from idmtools_platform_file.platform_operations.json_metadata_operations import \
    JSONMetadataOperations as FileJSONMetadataOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmJSONMetadataOperations(FileJSONMetadataOperations):
    platform: 'SlurmPlatform'  # noqa: F821
