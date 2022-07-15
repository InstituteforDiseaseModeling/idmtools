"""
Here we implement the SlurmPlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import Any, List, Type, Dict
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import SuiteDict


@dataclass
class SlurmPlatformSuiteOperations(IPlatformSuiteOperations):
    """
    Provides Suite operation to the SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
    platform_type: Type = field(default=SuiteDict)

    def get(self, suite_id: UUID, **kwargs) -> Dict:
        """
        Get an suite from the Slurm platform.
        Args:
            suite_id: Suite id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Suite object
        """
        raise NotImplementedError("Fetching suite has not been implemented on the Slurm Platform")

    def platform_create(self, suite: Suite, **kwargs) -> Dict:
        """
        Create suite on Slurm Platform.
        Args:
            suite: idmtools suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Suite object created
        """
        if not isinstance(suite.uid, UUID):
            suite.uid = uuid4()
        self.platform._op_client.mk_directory(suite)
        self.platform._metas.dump(suite)

        meta = self.platform._metas.get(suite)
        return SuiteDict(meta)

    def platform_run_item(self, suite: Suite, **kwargs):
        """
        Called during commissioning of an item. This should perform what is needed to commission job on platform.

        Args:
            suite:

        Returns:
            None
        """
        # Refresh with entity ids
        self.platform._metas.dump(suite)

    def get_parent(self, suite: SuiteDict, **kwargs) -> Any:
        """
        Fetches the parent of a suite.
        Args:
            suite: Slurm suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        return None

    def get_children(self, suite: Dict, parent: Suite = None, **kwargs) -> List[Dict]:
        """
        Fetch Slurm suite's children.
        Args:
            suite: Slurm suite
            parent: the parent of the experiments
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of Slurm experiments
        """
        raise NotImplementedError("Get children has not been implemented on the Slurm Platform")

    def refresh_status(self, suite: Suite, **kwargs):
        """
        Refresh the status of a suite. On comps, this is done by refreshing all experiments.
        Args:
            suite: idmtools suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh statu has not been implemented on the Slurm Platform")
