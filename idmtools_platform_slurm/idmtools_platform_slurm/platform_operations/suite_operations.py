"""
Here we implement the SlurmPlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Type, Dict, Tuple
from idmtools.core import ItemType
from idmtools.core import EntityStatus
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmSuite, SlurmExperiment

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform


@dataclass
class SlurmPlatformSuiteOperations(IPlatformSuiteOperations):
    """
    Provides Suite operation to the SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
    platform_type: Type = field(default=SlurmSuite)

    def get(self, suite_id: UUID, **kwargs) -> Dict:
        """
        Get a suite from the Slurm platform.
        Args:
            suite_id: Suite id
            kwargs: keyword arguments used to expand functionality
        Returns:
            Slurm Suite object
        """
        metas = self.platform._metas.filter(item_type=ItemType.SUITE, property_filter={'id': str(suite_id)})
        if len(metas) > 0:
            return SlurmSuite(metas[0])
        else:
            raise RuntimeError(f"Not found Suite with id '{suite_id}'")

    def platform_create(self, suite: Suite, **kwargs) -> Tuple:
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
        slurm_suite = SlurmSuite(meta)
        return slurm_suite, slurm_suite.id

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

    def get_parent(self, suite: SlurmSuite, **kwargs) -> Any:
        """
        Fetches the parent of a suite.
        Args:
            suite: Slurm suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        return None

    def get_children(self, suite: SlurmSuite, parent: Suite = None, **kwargs) -> List[SlurmExperiment]:
        """
        Fetch Slurm suite's children.
        Args:
            suite: Slurm suite
            parent: the parent of the experiments
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of Slurm experiments
        """
        exp_list = []
        exp_meta_list = self.platform._metas.get_children(parent)
        for meta in exp_meta_list:
            exp = self.platform._experiments.to_entity(SlurmExperiment(meta), parent=parent)
            exp_list.append(exp)
        return exp_list

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

    def to_entity(self, slurm_suite: SlurmSuite, children: bool = True, **kwargs) -> Suite:
        """
        Convert a SlurmSuite object to idmtools Suite.
        Args:
            slurm_suite: simulation to convert
            children: bool True/False
            kwargs: keyword arguments used to expand functionality
        Returns:
            Suite object
        """
        suite = Suite()
        suite.platform = self.platform
        suite.uid = UUID(slurm_suite.uid)
        suite.name = slurm_suite.name
        suite.parent = None
        suite.tags = slurm_suite.tags
        suite._platform_object = slurm_suite
        if children:
            suite.experiments = self.get_children(slurm_suite, parent=suite)
        return suite
