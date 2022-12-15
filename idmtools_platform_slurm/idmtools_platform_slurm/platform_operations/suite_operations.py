"""
Here we implement the SlurmPlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import shutil
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Type, Dict, Tuple
from logging import getLogger
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import SlurmSuite, SlurmExperiment

if TYPE_CHECKING:
    from idmtools_platform_slurm.slurm_platform import SlurmPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class SlurmPlatformSuiteOperations(IPlatformSuiteOperations):
    """
    Provides Suite operation to the SlurmPlatform.
    """
    platform: 'SlurmPlatform'  # noqa F821
    platform_type: Type = field(default=SlurmSuite)

    def get(self, suite_id: str, **kwargs) -> Dict:
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
        # Generate Suite folder structure
        self.platform._op_client.mk_directory(suite, exist_ok=False)
        self.platform._metas.dump(suite)

        # Return Slurm Suite
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

    def get_children(self, suite: SlurmSuite, parent: Suite = None, raw=True, **kwargs) -> List[Any]:
        """
        Fetch Slurm suite's children.
        Args:
            suite: Slurm suite
            raw: True/False
            parent: the parent of the experiments
            kwargs: keyword arguments used to expand functionality
        Returns:
            List of Slurm experiments
        """
        exp_list = []
        exp_meta_list = self.platform._metas.get_children(parent)
        for meta in exp_meta_list:
            slurm_exp = SlurmExperiment(meta)
            if raw:
                exp_list.append(slurm_exp)
            else:
                exp = self.platform._experiments.to_entity(slurm_exp, parent=parent)
                exp_list.append(exp)
        return exp_list

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
        suite.uid = slurm_suite.uid
        suite.name = slurm_suite.name
        suite.parent = None
        suite.tags = slurm_suite.tags
        suite._platform_object = slurm_suite
        suite.experiments = []

        if children:
            suite.experiments = self.get_children(slurm_suite, parent=suite, raw=False)
        return suite

    def refresh_status(self, suite: Suite, **kwargs):
        """
        Refresh the status of a suite. On comps, this is done by refreshing all experiments.
        Args:
            suite: idmtools suite
            kwargs: keyword arguments used to expand functionality
        Returns:
            None
        """
        for experiment in suite.experiments:
            self.platform.refresh_status(experiment, **kwargs)

    def create_sim_directory_map(self, suite_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            suite_id: suite id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        # s = Suite.get(suite_id)
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False, force=True)
        exps = suite.experiments
        sims_map = {}
        for exp in exps:
            d = self.platform._experiments.create_sim_directory_map(exp.id)
            sims_map = {**sims_map, **d}
        return sims_map

    def platform_delete(self, suite_id: str) -> None:
        """
        Delete platform suite.
        Args:
            suite_id: platform suite id
        Returns:
            None
        """
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        exps = suite.experiments
        for exp in exps:
            try:
                shutil.rmtree(self.platform._op_client.get_directory(exp))
            except RuntimeError:
                logger.info("Could not delete the associated experiment...")
                return
        try:
            shutil.rmtree(self.platform._op_client.get_directory(suite))
        except RuntimeError:
            logger.info(f"Could not delete suite ({suite_id})...")
            return

    def platform_cancel(self, suite_id: str, force: bool = False) -> None:
        """
        Cancel platform suite's slurm job.
        Args:
            suite_id: suite id
            force: bool, True/False
        Returns:
            None
        """
        suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=False)
        logger.debug(f"cancel slurm job for suite: {suite_id}...")
        for exp in suite.experiments:
            self.platform._experiments.platform_cancel(exp.id, force)
