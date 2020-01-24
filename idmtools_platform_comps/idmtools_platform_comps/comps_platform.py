import copy
import json
import logging
import typing
from dataclasses import dataclass, field
from COMPS import Client
from idmtools.core import CacheEnabled, ItemType
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iexperiment import IExperiment, IGPUExperiment, IDockerExperiment, \
    ILinuxExperiment
from idmtools_platform_comps.comps_operations.asset_collection_operations import \
    CompsPlatformAssetCollectionOperations
from idmtools_platform_comps.comps_operations.experiment_operations import CompsPlatformExperimentOperations
from idmtools_platform_comps.comps_operations.simulation_operations import CompsPlatformSimulationOperations
from idmtools_platform_comps.comps_operations.suite_operations import CompsPlatformSuiteOperations
from idmtools_platform_comps.comps_operations.workflow_item_operations import CompsPlatformWorkflowItemOperations
from idmtools.entities.platform_requirements import PlatformRequirements
from typing import List

logging.getLogger('COMPS.Data.Simulation').disabled = True
logger = logging.getLogger(__name__)


class COMPSPriority:
    Lowest = "Lowest"
    BelowNormal = "BelowNormal"
    Normal = "Normal"
    AboveNormal = "AboveNormal"
    Highest = "Highest"


op_defaults = dict(default=None, compare=False, metadata=dict(pickle_ignore=True))


supported_types = [PlatformRequirements.DOCKER, PlatformRequirements.PYTHON, PlatformRequirements.SHELL,
                   PlatformRequirements.NativeBinary, PlatformRequirements.WINDOWS]


@dataclass
class COMPSPlatform(IPlatform, CacheEnabled):
    """
    Represents the platform allowing to run simulations on COMPS.
    """

    MAX_SUBDIRECTORY_LENGTH = 35  # avoid maxpath issues on COMPS

    endpoint: str = field(default="https://comps2.idmod.org")
    environment: str = field(default="Bayesian")
    priority: str = field(default=COMPSPriority.Lowest)
    simulation_root: str = field(default="$COMPS_PATH(USER)\\output")
    node_group: str = field(default="emod_abcd")
    num_retires: int = field(default=0)
    num_cores: int = field(default=1)
    exclusive: bool = field(default=False)

    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types))

    _experiments: CompsPlatformExperimentOperations = field(**op_defaults)
    _simulations: CompsPlatformSimulationOperations = field(**op_defaults)
    _suites: CompsPlatformSuiteOperations = field(**op_defaults)
    _workflow_items: CompsPlatformWorkflowItemOperations = field(**op_defaults)
    _assets: CompsPlatformAssetCollectionOperations = field(**op_defaults)

    def __post_init__(self):
        print("\nUser Login:")
        print(json.dumps({"endpoint": self.endpoint, "environment": self.environment}, indent=3))
        self.__init_interfaces()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.SUITE, ItemType.ASSETCOLLECTION}
        super().__post_init__()

    def __init_interfaces(self):
        self._login()
        self._experiments = CompsPlatformExperimentOperations(platform=self)
        self._simulations = CompsPlatformSimulationOperations(platform=self)
        self._suites = CompsPlatformSuiteOperations(platform=self)
        self._workflow_items = CompsPlatformWorkflowItemOperations(platform=self)
        self._assets = CompsPlatformAssetCollectionOperations(platform=self)

    def _login(self):
        try:
            Client.auth_manager()
        except RuntimeError:
            Client.login(self.endpoint)

    def supported_experiment_types(self) -> List[typing.Type]:
        return [IExperiment]

    def unsupported_experiment_types(self) -> List[typing.Type]:
        return [IDockerExperiment, IGPUExperiment, ILinuxExperiment]

    def post_setstate(self):
        self.__init_interfaces()
