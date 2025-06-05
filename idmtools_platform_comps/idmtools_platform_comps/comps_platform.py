"""idmtools COMPSPlatform.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
# flake8: noqa E402
import copy
import logging

# fix for comps weird import
from idmtools.entities.simulation import Simulation

HANDLERS = copy.copy(logging.getLogger().handlers)
LEVEL = logging.getLogger().level
from COMPS import Client

comps_logger = logging.getLogger('COMPS')
logging.root.handlers = HANDLERS
logging.getLogger().setLevel(LEVEL)
comps_logger.propagate = False
comps_logger.handlers = [h for h in comps_logger.handlers if isinstance(h, logging.FileHandler)]
from COMPS.Data import Simulation as COMPSSimulation
from COMPS.Data import WorkItem as COMPSWorkItem
from COMPS.Data import AssetCollection as COMPSAssetCollection
from COMPS.Data import Experiment as COMPSExperiment
from COMPS.Data import Suite as COMPSSuite
from COMPS.Data.Simulation import SimulationState
from COMPS.Data.WorkItem import WorkItemState
from idmtools.assets.asset_collection import AssetCollection
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.iplatform_default import AnalyzerManagerPlatformDefault, IPlatformDefault
from idmtools.entities.iworkflow_item import IWorkflowItem
from dataclasses import dataclass, field
from typing import Union, Dict, Set
from functools import partial
from typing import List
from enum import Enum
from idmtools.core import CacheEnabled, ItemType, EntityStatus
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools_platform_comps.comps_operations.asset_collection_operations import CompsPlatformAssetCollectionOperations
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
SLURM_ENVS = ['calculon', 'slurmstage', "slurmdev", "nibbler"]
supported_types = [PlatformRequirements.PYTHON, PlatformRequirements.SHELL, PlatformRequirements.NativeBinary]
PLATFORM_DEFAULTS = [AnalyzerManagerPlatformDefault(max_workers=24)]


@dataclass(repr=False)
class COMPSPlatform(IPlatform, CacheEnabled):
    """
    Represents the platform allowing to run simulations on COMPS.
    """

    MAX_SUBDIRECTORY_LENGTH = 35  # avoid maxpath issues on COMPS

    endpoint: str = field(default="https://comps.idmod.org", metadata={"help": "URL of the COMPS endpoint to use"})
    environment: str = field(default="Calculon",
                             metadata=dict(help="Name of the COMPS environment to target", callback=environment_list))
    priority: str = field(default=COMPSPriority.Lowest.value,
                          metadata=dict(help="Priority of the job", choices=[p.value for p in COMPSPriority]))
    simulation_root: str = field(default="$COMPS_PATH(USER)\\output", metadata=dict(help="Location of the outputs"))
    node_group: str = field(default=None, metadata=dict(help="Node group to target"))
    num_retries: int = field(default=0, metadata=dict(help="How retries if the simulation fails",
                                                      validate=partial(validate_range, min=0, max=10)))
    num_cores: int = field(default=1, metadata=dict(help="How many cores per simulation",
                                                    validate=partial(validate_range, min=1, max=32)))
    max_workers: int = field(default=16, metadata=dict(help="How many processes to spawn locally",
                                                       validate=partial(validate_range, min=1, max=32)))
    batch_size: int = field(default=10, metadata=dict(help="How many simulations per batch",
                                                      validate=partial(validate_range, min=1, max=100)))
    min_time_between_commissions: int = field(default=15, metadata=dict(
        help="How many seconds between commission calls on an experiment",
        validate=partial(validate_range, min=10, max=300)))
    exclusive: bool = field(default=False,
                            metadata=dict(help="Enable exclusive mode? (one simulation per node on the cluster)"))
    docker_image: str = field(default=None, metadata={"help": "Docker image to use for simulations"})

    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types),
                                                           repr=False, init=False)
    _platform_defaults: List[IPlatformDefault] = field(default_factory=lambda: copy.deepcopy(PLATFORM_DEFAULTS))

    _experiments: CompsPlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: CompsPlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _suites: CompsPlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _workflow_items: CompsPlatformWorkflowItemOperations = field(**op_defaults, repr=False, init=False)
    _assets: CompsPlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)
    _skip_login: bool = field(default=False, repr=False)

    def __post_init__(self):
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
        if not self._skip_login:
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

    def get_workitem_link(self, work_item: IWorkflowItem):
        return f"{self.endpoint}/#explore/WorkItems?filters=Id={work_item.uid}"

    def get_asset_collection_link(self, asset_collection: AssetCollection):
        return f"{self.endpoint}/#explore/AssetCollections?filters=Id={asset_collection.uid}"

    def get_username(self):
        return Client.auth_manager()._username

    def is_windows_platform(self, item: IEntity = None) -> bool:
        if isinstance(item, IWorkflowItem):
            return False
        return super().is_windows_platform(item)

    def validate_item_for_analysis(self, item: object, analyze_failed_items=False):
        """
        Check if item is valid for analysis.

        Args:
            item: which item to flatten
            analyze_failed_items: bool

        Returns: bool
        """
        result = False
        if isinstance(item, COMPSSimulation):
            if item.state == SimulationState.Succeeded:
                result = True
            else:
                if analyze_failed_items and item.state == SimulationState.Failed:
                    result = True
        elif isinstance(item, COMPSWorkItem):
            if item.state == WorkItemState.Succeeded:
                result = True
            else:
                if analyze_failed_items and item.state == WorkItemState.Failed:
                    result = True
        elif isinstance(item, (Simulation, IWorkflowItem)):
            if item.succeeded:
                result = True
            else:
                if analyze_failed_items and item.status == EntityStatus.FAILED:
                    result = True

        return result

    def get_files(self, item: Union[COMPSSimulation, COMPSWorkItem, COMPSAssetCollection], files: Union[Set[str], List[str]], output: str = None, **kwargs) -> \
            Union[Dict[str, Dict[str, bytearray]], Dict[str, bytearray]]:
        """
        Get files for a platform entity.

        Args:
            item: Item to fetch files for
            files: List of file names to get
            output: save files to
            kwargs: Platform arguments

        Returns:
            For simulations, this returns a dictionary with filename as key and values being binary data from file or a
            dict.

            For experiments, this returns a dictionary with key as sim id and then the values as a dict of the
            simulations described above
        """
        if not isinstance(item, (COMPSSimulation, COMPSWorkItem, COMPSAssetCollection, Simulation, IWorkflowItem,
                                 AssetCollection)):
            raise TypeError(f'Item Type: {type(item)} is not supported!')

        item = self.flatten_item(item, **kwargs)[0]
        file_data = super().get_files(item, files, output, **kwargs)
        return file_data

    def flatten_item(self, item: object, raw: bool = False, **kwargs) -> List[object]:
        """
        Flatten an item: resolve the children until getting to the leaves.

        For example, for an experiment, will return all the simulations.
        For a suite, will return all the simulations contained in the suites experiments.

        Args:
            item: Which item to flatten
            raw: If True, returns raw platform objects, False, return local objects
            kwargs: Extra parameters for conversion

        Returns:
            List of leaf items, which can be from either the local platform or a COMPS server:
            - Simulations (either local Simulation or COMPSSimulation),
            - WorkItems (local or COMPSWorkItem),
            - or AssetCollections (local or COMPSAssetCollection).
        """
        # Return directly if item is already in leaf and raw = False
        if not raw and isinstance(item, (Simulation, IWorkflowItem, AssetCollection)):
            return [item]
        # Handle platform object conversion if needed
        if not isinstance(item, (COMPSSuite, COMPSExperiment, COMPSSimulation,
                                 COMPSWorkItem, COMPSAssetCollection)):
            return self.flatten_item(item.get_platform_object(), raw=raw, **kwargs)

        # Process types (suites and experiments)
        if isinstance(item, (COMPSSuite, COMPSExperiment)):
            children = self._get_children_for_platform_item(item, children=["tags", "configuration"])
            # Assign server experiment to child.experiment to avoid recreating child's parent
            if isinstance(item, COMPSExperiment):
                item = self._normalized_item_fields(item)
                for child in children:
                    child.experiment = item

            return [leaf
                for child in children
                for leaf in self.flatten_item(child, raw=raw, **kwargs)]

        # Handle leaf types
        if isinstance(item, (COMPSSimulation, COMPSWorkItem, COMPSAssetCollection)):
            if isinstance(item, COMPSSimulation):
                self._ensure_simulation_experiment(item)
            item = self._normalized_item_fields(item)

        if not raw:
            parent = item.experiment if isinstance(item, COMPSSimulation) else None
            item = self._convert_platform_item_to_entity(item, parent=parent, **kwargs)

        return [item]

    def _ensure_simulation_experiment(self, simulation):
        """Ensure simulation has a valid experiment attached."""
        if not hasattr(simulation, "experiment") or simulation.experiment.configuration is None:
            experiment = self.get_item(simulation.experiment_id,
                                       item_type=ItemType.EXPERIMENT,
                                       raw=True)
            simulation.experiment = self._normalized_item_fields(experiment)

    def _normalized_item_fields(self, item):
        item.uid = item.id
        item._id = str(item.id)
        if type(item).__name__ == "WorkItem":
            item.item_type = ItemType.WORKFLOW_ITEM
        elif type(item).__name__ == "AssetCollection":
            item.item_type = ItemType.ASSETCOLLECTION
        else:
            item.item_type = ItemType(type(item).__name__)
        item.platform = self
        item._platform_object = item
        return item