from dataclasses import dataclass, field

from idmtools_platform_comps.comps_operations.asset_collection_operations import CompsPlatformAssetCollectionOperations
from idmtools_platform_comps.comps_operations.experiment_operations import CompsPlatformExperimentOperations
from idmtools_platform_comps.comps_operations.suite_operations import CompsPlatformSuiteOperations
from idmtools_platform_comps.comps_platform import COMPSPlatform, op_defaults
from idmtools_platform_comps.ssmt_operations.simulation_operations import SSMTPlatformSimulationOperations
from idmtools_platform_comps.ssmt_operations.workflow_item_operations import SSMTPlatformWorkflowItemOperations


@dataclass
class SSMTPlatform(COMPSPlatform):
    """
    Represents the platform allowing to run simulations on SSMT.
    """

    _simulations: SSMTPlatformSimulationOperations = field(**op_defaults)
    _workflow_items: SSMTPlatformWorkflowItemOperations = field(**op_defaults)

    def __init_interfaces(self):
        self._experiments = CompsPlatformExperimentOperations(platform=self)
        self._simulations = SSMTPlatformSimulationOperations(platform=self)
        self._suites = CompsPlatformSuiteOperations(platform=self)
        self._workflow_items = SSMTPlatformWorkflowItemOperations(platform=self)
        self._assets = CompsPlatformAssetCollectionOperations(platform=self)