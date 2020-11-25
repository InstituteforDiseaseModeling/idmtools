from dataclasses import field, dataclass
from typing import Any, List, Tuple, Type
from uuid import UUID
from idmtools.entities import Suite
from idmtools.entities.iplatform_ops.iplatform_suite_operations import IPlatformSuiteOperations


# Class to distinguish between regular AC and our platform and for type mapping on the platform
class FilePlatformSuite(Suite):
    pass


@dataclass
class FilePlatformSuiteOperations(IPlatformSuiteOperations):
    platform: 'FilePlatform'  # noqa F821
    platform_type: Type = field(default=FilePlatformSuite)

    def get(self, suite_id: UUID, **kwargs) -> Any:
        pass

    def platform_create(self, suite: Suite, **kwargs) -> Tuple[Any, UUID]:
        pass

    def get_parent(self, suite: Any, **kwargs) -> Any:
        pass

    def get_children(self, suite: Any, **kwargs) -> List[Any]:
        pass

    def refresh_status(self, experiment: Suite, **kwargs):
        pass
