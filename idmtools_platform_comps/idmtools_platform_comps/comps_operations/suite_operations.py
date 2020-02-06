from dataclasses import dataclass, field
from typing import Any, List, Tuple, Union, Type
from uuid import UUID

from COMPS.Data import Suite as COMPSSuite, QueryCriteria, Experiment as COMPSExperiment, WorkItem

from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations


@dataclass
class CompsPlatformSuiteOperations(IPlatformSuiteOperations):
    platform: 'COMPSPlaform'  # noqa F821
    platform_type: Type = field(default=COMPSSuite)

    def get(self, suite_id: UUID, **kwargs) -> COMPSSuite:
        cols = kwargs.get('columns')
        children = kwargs.get('children')
        cols = cols or ["id", "name"]
        children = children if children is not None else ["tags", "configuration"]
        # Comps doesn't like getting uuids for some reason
        s = COMPSSuite.get(id=str(suite_id), query_criteria=QueryCriteria().select(cols).select_children(children))
        return s

    def platform_create(self, suite: Suite, **kwargs) -> Tuple[COMPSSuite, UUID]:
        self.platform._login()

        # Create suite
        comps_suite = COMPSSuite(name=suite.name, description=suite.description)
        comps_suite.set_tags(suite.tags)
        comps_suite.save()

        # Update suite uid
        suite.uid = comps_suite.id
        return comps_suite, suite.uid

    def get_parent(self, suite: COMPSSuite, **kwargs) -> Any:
        return None

    def get_children(self, suite: COMPSSuite, **kwargs) -> List[Union[COMPSExperiment, WorkItem]]:
        cols = kwargs.get("cols")
        children = kwargs.get("children")
        cols = cols or ["id", "name", "suite_id"]
        children = children if children is not None else ["tags"]

        children = suite.get_experiments(query_criteria=QueryCriteria().select(cols).select_children(children))
        return children

    def refresh_status(self, suite: Suite, **kwargs):
        pass

    def to_entity(self, suite: Any, **kwargs) -> Suite:
        # Creat a suite
        obj = Suite()

        # Set its correct attributes
        obj.uid = suite.id
        obj.name = suite.name
        obj.description = suite.description
        obj.tags = suite.tags
        obj.comps_suite = suite
        return obj
