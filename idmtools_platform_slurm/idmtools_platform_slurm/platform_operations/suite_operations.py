"""
Here we implement the SlurmPlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import Any, List, Type, Dict
from idmtools.core import EntityStatus
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import SuiteDict, ExperimentDict


@dataclass
class SlurmPlatformSuiteOperations(IPlatformSuiteOperations):
    """
    Provides Suite operation to the SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
    platform_type: Type = field(default=SuiteDict)

    def get(self, suite_id: UUID, **kwargs) -> Dict:
        """
        Get Suite.
        Args:
            suite_id: Suite id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Suite
        """
        raise NotImplementedError("Fetching suite has not been implemented on the Slurm Platform")

    def platform_create(self, suite: Suite, **kwargs) -> Dict:
        """
        Create suite on Slurm Platform.
        Args:
            suite: Suite to create
            kwargs: keyword arguments used to expand functionality
        Returns:
            Suite object
        """
        # Create suite
        # suite.uid = str(uuid4())
        # if not Path(self.platform.job_directory, suite.id).exists():
        # if not self.platform._op_client.get_directory(suite).exists():
        # if not self.platform._op_client.item_exist(suite):
        if not isinstance(suite.uid, UUID):
            suite.uid = uuid4()
        # suite.status = EntityStatus.CREATED
        # self.platform._suites.create_entity_tree(suite)
        self.platform._op_client.mk_directory(suite)
        self.platform._metas.dump(suite)

        meta = self.platform._metas.get(suite)
        return SuiteDict(meta)

    def get_parent(self, suite: Suite, **kwargs) -> Any:
        """
        Fetches the parent of a suite.
        Args:
            suite: Suite to get parent of
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        return None

    def get_children(self, slurm_suite: Dict, parent: Suite = None, **kwargs) -> List[Experiment]:
        """
        Get children for a suite.
        Args:
            slurm_suite: Suite to get children for
            parent:
            kwargs: keyword arguments used to expand functionality
        Returns:
            List Experiments that are part of the suite
        """
        raise NotImplementedError("Get children has not been implemented on the Slurm Platform")

    def refresh_status(self, suite: Suite, **kwargs):
        """
        Refresh the status of a suite. On comps, this is done by refreshing all experiments.
        Args:
            suite: Suite to refresh status of
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        raise NotImplementedError("Refresh statu has not been implemented on the Slurm Platform")
