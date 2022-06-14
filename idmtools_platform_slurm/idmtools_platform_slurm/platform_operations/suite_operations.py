"""
Here we implement the SlurmPlatform suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# from pathlib import Path
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import Any, List, Type, Dict
from idmtools.core import ItemType
from idmtools.core import EntityStatus
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations
from idmtools_platform_slurm.platform_operations.utils import SuiteDict, ExperimentDict

# METADATA_FILE = 'metadata.json'


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
        # raise NotImplementedError("Fetching suite has not been implemented on the Slurm Platform")

        # suite_dir = Path(self.platform.job_directory, str(suite_id))
        # if suite_dir.exists():
        #     meta_file = Path(suite_dir, METADATA_FILE)
        #     meta = self.platform._metas.load_from_file(meta_file)
        #     return SuiteDict(meta)

        metas = self.platform._metas.filter(item_type=ItemType.SUITE, property_filter={'id': str(suite_id)})
        if len(metas) > 0:
            return SuiteDict(metas[0])
        else:
            raise RuntimeError(f"Not found Suite with id '{suite_id}'")

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
        # raise NotImplementedError("Get children has not been implemented on the Slurm Platform")

        exp_list = []
        exp_meta_list = self.platform._metas.get_children(parent)
        for meta in exp_meta_list:
            exp = self.platform._experiments.to_entity(ExperimentDict(meta), parent=parent)
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

    def to_entity(self, slurm_suite: Dict, children: bool = True, **kwargs) -> Suite:
        """
        Convert a sim dict object to an ISimulation.
        Args:
            slurm_suite: simulation to convert
            parent: optional experiment object
            children: bool
            kwargs:
        Returns:
            Suite object
        """
        suite = Suite()
        suite.platform = self.platform
        suite._uid = UUID(slurm_suite['uid'])
        # suite.uid = suite_meta['id']
        suite.name = slurm_suite['name']
        suite.parent = None
        suite.tags = slurm_suite['tags']
        suite._platform_object = slurm_suite
        suite.status = EntityStatus[slurm_suite['status']] if slurm_suite['status'] else EntityStatus.CREATED
        if children:
            suite.experiments = self.get_children(slurm_suite, parent=suite)

        return suite
