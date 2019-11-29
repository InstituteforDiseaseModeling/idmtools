import json
import logging
import typing
from dataclasses import dataclass, field
from COMPS import Client
from idmtools.core import CacheEnabled, ItemType
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import IExperiment, IGPUExperiment, IDockerExperiment, \
    ILinuxExperiment
from idmtools_platform_comps.comps_commision_operations import COMPSPlatformCommissionOperations
from idmtools_platform_comps.comps_io_operations import COMPSPlatformIOOperations
from typing import List

from idmtools_platform_comps.comps_metadata_operations import COMPSMetaDataOperations

logging.getLogger('COMPS.Data.Simulation').disabled = True
logger = logging.getLogger(__name__)


class COMPSPriority:
    Lowest = "Lowest"
    BelowNormal = "BelowNormal"
    Normal = "Normal"
    AboveNormal = "AboveNormal"
    Highest = "Highest"


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

    io: COMPSPlatformIOOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})
    commissioning: COMPSPlatformCommissionOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})
    metadata: COMPSMetaDataOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})

    def __post_init__(self):
        print("\nUser Login:")
        print(json.dumps({"endpoint": self.endpoint, "environment": self.environment}, indent=3))
        self._login()
        self.__init_interfaces()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.SUITE, ItemType.ASSETCOLLECTION}
        super().__post_init__()

    def __init_interfaces(self):
        self.io = COMPSPlatformIOOperations(parent=self)
        self.commissioning = COMPSPlatformCommissionOperations(parent=self)
        self.metadata = COMPSMetaDataOperations(parent=self)

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
