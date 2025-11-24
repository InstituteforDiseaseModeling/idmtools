"""
Here we implement the SlurmPlatform suite operations.

Copyright 2025, Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING
from logging import getLogger
from idmtools.core import ItemType
from idmtools_platform_file.platform_operations.suite_operations import FilePlatformSuiteOperations

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class SlurmPlatformSuiteOperations(FilePlatformSuiteOperations):
    """
    Provides Suite operation to the SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821

    def platform_cancel(self, suite_id: str, force: bool = False) -> None:
        """
        Cancel platform suite's slurm job.
        Args:
            suite_id: suite id
            force: bool, True/False
        Returns:
            None
        """
        suite = self.platform.get_item(suite_id, ItemType.SUITE, force=True, raw=False)
        logger.debug(f"cancel slurm job for suite: {suite_id}...")
        for exp in suite.experiments:
            self.platform._experiments.platform_cancel(exp.id, force)
