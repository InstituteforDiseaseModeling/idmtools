"""idmtools comps suite operations.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import dataclass, field
from typing import Any, List, Dict, Tuple, Union, Type, TYPE_CHECKING, Optional
from uuid import UUID
from logging import getLogger
from COMPS.Data import Suite as COMPSSuite, QueryCriteria, Experiment as COMPSExperiment, WorkItem
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations

if TYPE_CHECKING:  # pragma: no cover
    from idmtools_platform_comps.comps_platform import COMPSPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class CompsPlatformSuiteOperations(IPlatformSuiteOperations):
    """
    Provides Suite operation to the COMPSPlatform.
    """
    platform: 'COMPSPlatform'  # noqa F821
    platform_type: Type = field(default=COMPSSuite)

    def get(self, suite_id: UUID, columns: Optional[List[str]] = None, load_children: Optional[List[str]] = None,
            query_criteria: Optional[QueryCriteria] = None, **kwargs) -> COMPSSuite:
        """
        Get COMPS Suite.

        Args:
            suite_id: Suite id 
            columns:  Optional list of columns. Defaults to id and name
            load_children: Optional list of children to load. Defaults to "tags", "configuration"
            query_criteria: Optional query criteria
            **kwargs: 

        Returns:
            COMPSSuite
        """
        columns = columns or ["id", "name"]
        children = load_children if load_children is not None else ["tags", "configuration"]
        # Comps doesn't like getting uuids for some reason
        query_criteria = query_criteria or QueryCriteria().select(columns).select_children(children)
        s = COMPSSuite.get(id=str(suite_id), query_criteria=query_criteria)
        return s

    def platform_create(self, suite: Suite, **kwargs) -> Tuple[COMPSSuite, UUID]:
        """
        Create suite on COMPS.

        Args:
            suite: Suite to create
            **kwargs:

        Returns:
            COMPS Suite object and a UUID
        """
        self.platform._login()

        # Create suite
        comps_suite = COMPSSuite(name=suite.name, description=suite.description)
        comps_suite.set_tags(suite.tags)
        comps_suite.save()

        # Update suite uid
        suite.uid = comps_suite.id
        return comps_suite, suite.uid

    def get_parent(self, suite: COMPSSuite, **kwargs) -> Any:
        """
        Get parent of suite. We always return None on COMPS.

        Args:
            suite:Suite to get parent of
            **kwargs:

        Returns:
            None
        """
        return None

    def get_children(self, suite: COMPSSuite, **kwargs) -> List[Union[COMPSExperiment, WorkItem]]:
        """
        Get children for a suite.

        Args:
            suite: Suite to get children for
            **kwargs: Any arguments to pass on to loading functions

        Returns:
            List of COMPS Experiments/Workitems that are part of the suite
        """
        cols = kwargs.get("cols")
        children = kwargs.get("children")
        cols = cols or ["id", "name", "suite_id"]
        children = children if children is not None else ["tags"]

        children = suite.get_experiments(query_criteria=QueryCriteria().select(cols).select_children(children))
        return children

    def refresh_status(self, suite: Suite, **kwargs):
        """
        Refresh the status of a suite. On comps, this is done by refreshing all experiments.

        Args:
            suite: Suite to refresh status of
            **kwargs:

        Returns:
            None
        """
        for experiment in suite.experiments:
            self.platform.refresh_status(experiment)

    def to_entity(self, suite: COMPSSuite, children: bool = True, **kwargs) -> Suite:
        """
        Convert a COMPS Suite to an IDM Suite.

        Args:
            suite: Suite to Convert
            children: When true, load simulations, false otherwise
            **kwargs:

        Returns:
            IDM Suite
        """
        # Creat a suite
        obj = Suite()

        # Set its correct attributes
        obj.uid = suite.id
        obj.name = suite.name
        obj.description = suite.description
        obj.tags = suite.tags
        obj.comps_suite = suite

        # Convert all experiments
        if children:
            comps_exps = suite.get_experiments()
            obj.experiments = []
            for exp in comps_exps:
                self.platform._experiments.to_entity(exp, parent=obj, **kwargs)
        return obj

    def create_sim_directory_map(self, suite_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            suite_id: suite id

        Returns:
            Dict of simulation id as key and working dir as value
        """
        # s = Suite.get(suite_id)
        comps_suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True, force=True)
        comps_exps = comps_suite.get_experiments(QueryCriteria().select('id'))
        sims_map = {}
        for exp in comps_exps:
            r = self.platform._experiments.create_sim_directory_map(exp.id)
            sims_map = {**sims_map, **r}
        return sims_map

    def platform_delete(self, suite_id: str) -> None:
        """
        Delete platform suite.
        Args:
            suite_id: platform suite id
        Returns:
            None
        """
        comps_suite = self.platform.get_item(suite_id, ItemType.SUITE, raw=True)
        comps_exps = comps_suite.get_experiments()
        for comps_exp in comps_exps:
            try:
                comps_exp.delete()
            except RuntimeError:
                logger.info(f"Could not delete the associated experiment ({comps_exp.id})...")
                return
        try:
            comps_suite.delete()
        except RuntimeError:
            logger.info(f"Could not delete suite ({suite_id})...")
            return
