from dataclasses import dataclass, field
from idmtools_platform_comps.comps_platform import COMPSPlatform, op_defaults
from idmtools_platform_comps.ssmt_operations.simulation_operations import SSMTPlatformSimulationOperations
from idmtools_platform_comps.ssmt_operations.workflow_item_operations import SSMTPlatformWorkflowItemOperations
from idmtools_platform_comps.ssmt_operations.work_item_operations import SSMTPlatformWorkItemOperations


@dataclass(repr=False)
class SSMTPlatform(COMPSPlatform):
    """
    Represents the platform allowing to run simulations on SSMT.
    """

    item_type: str = field(default=None)
    docker_image: str = field(default=None)
    plugin_key: str = field(default=None)

    _work_items: SSMTPlatformWorkItemOperations = field(**op_defaults, repr=False, init=False)
    _simulations: SSMTPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _workflow_items: SSMTPlatformWorkflowItemOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        self.__init_interfaces()
        super().__post_init__()

    def __init_interfaces(self):
        self._work_items = SSMTPlatformWorkItemOperations(platform=self)
        self._simulations = SSMTPlatformSimulationOperations(platform=self)
        self._workflow_items = SSMTPlatformWorkflowItemOperations(platform=self)
