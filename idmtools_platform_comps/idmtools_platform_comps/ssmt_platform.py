"""define the ssmt platform.

SSMT platform is the same as the COMPS platform but file access is local.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
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

    def __post_init__(self):
        """
        Post method after SSMTPlatform creation.

        Returns: None
        """
        super().__post_init__()
        self.__init_interfaces()

    def __init_interfaces(self):
        """
        Initialize intefaces.

        Returns: None
        """
        self._experiments = CompsPlatformExperimentOperations(platform=self)
        self._simulations = SSMTPlatformSimulationOperations(platform=self)
        self._suites = CompsPlatformSuiteOperations(platform=self)
        self._workflow_items = SSMTPlatformWorkflowItemOperations(platform=self)
        self._assets = CompsPlatformAssetCollectionOperations(platform=self)
