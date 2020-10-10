# flake8: noqa E402
import copy
import json
import logging
# fix for comps weird import
handlers = copy.copy(logging.getLogger().handlers)
from COMPS import Client
logging.root.handlers = handlers
from dataclasses import dataclass, field
from functools import partial
from typing import List
from enum import Enum
from idmtools.core import CacheEnabled, ItemType
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools_platform_comps.comps_operations.asset_collection_operations import \
    CompsPlatformAssetCollectionOperations
from idmtools_platform_comps.comps_operations.experiment_operations import CompsPlatformExperimentOperations
from idmtools_platform_comps.comps_operations.simulation_operations import CompsPlatformSimulationOperations
from idmtools_platform_comps.comps_operations.suite_operations import CompsPlatformSuiteOperations
from idmtools_platform_comps.comps_operations.workflow_item_operations import CompsPlatformWorkflowItemOperations
from idmtools_platform_comps.cli.cli_functions import environment_list, validate_range

logger = logging.getLogger(__name__)


class COMPSPriority(Enum):
    Lowest = "Lowest"
    BelowNormal = "BelowNormal"
    Normal = "Normal"
    AboveNormal = "AboveNormal"
    Highest = "Highest"


op_defaults = dict(default=None, compare=False, metadata=dict(pickle_ignore=True))

# We use this to track os. It would be nice to do that in server
SLURM_ENVS = ['calculon', 'slurmstage', "slurmdev"]
supported_types = [PlatformRequirements.PYTHON, PlatformRequirements.SHELL, PlatformRequirements.NativeBinary]


@dataclass(repr=False)
class COMPSPlatform(IPlatform, CacheEnabled):
    """
    Represents the platform allowing to run simulations on COMPS.
    """

    MAX_SUBDIRECTORY_LENGTH = 35  # avoid maxpath issues on COMPS

    endpoint: str = field(default="https://comps2.idmod.org", metadata={"help": "URL of the COMPS endpoint to use"})
    environment: str = field(default="Bayesian",
                             metadata={"help": "Name of the COMPS environment to target", "callback": environment_list})
    priority: str = field(default=COMPSPriority.Lowest.value,
                          metadata={"help": "Priority of the job", "choices": [p.value for p in COMPSPriority]})
    simulation_root: str = field(default="$COMPS_PATH(USER)\\output", metadata={"help": "Location of the outputs"})
    node_group: str = field(default=None, metadata={"help": "Node group to target"})
    num_retries: int = field(default=0, metadata={"help": "How retries if the simulation fails",
                                                  "validate": partial(validate_range, min=0, max=10)})
    num_cores: int = field(default=1, metadata={"help": "How many cores per simulation",
                                                "validate": partial(validate_range, min=1, max=32)})
    max_workers: int = field(default=16, metadata={"help": "How many processes to spawn locally",
                                                   "validate": partial(validate_range, min=1, max=32)})
    batch_size: int = field(default=10, metadata={"help": "How many simulations per batch",
                                                  "validate": partial(validate_range, min=1, max=100)})
    min_time_between_commissions: int = field(default=15, metadata={
        "help": "How many seconds between commission calls on an experiment. ",
        "validate": partial(validate_range, min=10, max=300)})
    exclusive: bool = field(default=False,
                            metadata={"help": "Enable exclusive mode? (one simulation per node on the cluster)"})
    docker_image: str = field(default=None)

    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types),
                                                           repr=False, init=False)

    _experiments: CompsPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: CompsPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _suites: CompsPlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _workflow_items: CompsPlatformWorkflowItemOperations = field(**op_defaults, repr=False, init=False)
    _assets: CompsPlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        print("\nUser Login:")
        print(json.dumps({"endpoint": self.endpoint, "environment": self.environment}, indent=3))
        self.__init_interfaces()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION, ItemType.SUITE, ItemType.ASSETCOLLECTION,
                                ItemType.WORKFLOW_ITEM}
        super().__post_init__()
        # set platform requirements based on environment
        if self.environment.lower() in SLURM_ENVS:
            self._platform_supports.append(PlatformRequirements.LINUX)
        else:
            self._platform_supports.append(PlatformRequirements.WINDOWS)

    def __init_interfaces(self):
        self._login()
        self._experiments = CompsPlatformExperimentOperations(platform=self)
        self._simulations = CompsPlatformSimulationOperations(platform=self)
        self._suites = CompsPlatformSuiteOperations(platform=self)
        self._workflow_items = CompsPlatformWorkflowItemOperations(platform=self)
        self._assets = CompsPlatformAssetCollectionOperations(platform=self)

    def _login(self):
        # ensure logging is initialized
        from idmtools.core.logging import exclude_logging_classes
        exclude_logging_classes()
        Client.login(self.endpoint)

    def post_setstate(self):
        self.__init_interfaces()
