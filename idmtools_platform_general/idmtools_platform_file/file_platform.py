"""
Here we implement the FilePlatform object.

Copyright 2025, Gates Foundation. All rights reserved.
"""
import os
from pathlib import Path
from logging import getLogger
from typing import Union, List
from dataclasses import dataclass, field

from idmtools import IdmConfigParser
from idmtools.core import ItemType, EntityStatus, TRUTHY_VALUES
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.iplatform import IPlatform, ITEM_TYPE_TO_OBJECT_INTERFACE
from idmtools_platform_file.file_operations.file_operations import FileOperations
from idmtools_platform_file.platform_operations.asset_collection_operations import FilePlatformAssetCollectionOperations
from idmtools_platform_file.platform_operations.experiment_operations import FilePlatformExperimentOperations
from idmtools_platform_file.platform_operations.json_metadata_operations import JSONMetadataOperations
from idmtools_platform_file.platform_operations.simulation_operations import FilePlatformSimulationOperations
from idmtools_platform_file.platform_operations.suite_operations import FilePlatformSuiteOperations
from idmtools_platform_file.platform_operations.utils import FileExperiment, FileSimulation, FileSuite

logger = getLogger(__name__)
user_logger = getLogger('user')

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})


@dataclass(repr=False)
class FilePlatform(IPlatform):
    """
    File Platform definition.
    """
    job_directory: str = field(default=None, metadata=dict(help="Job Directory"))
    max_job: int = field(default=4, metadata=dict(help="Maximum number of jobs to run concurrently"))
    run_sequence: bool = field(default=True, metadata=dict(help="Run jobs in sequence"))
    sym_link: bool = field(default=True, metadata=dict(help="Use symbolic links"))
    # Default retries for jobs
    retries: int = field(default=1, metadata=dict(help="Number of retries for failed jobs"))
    # number of MPI processes
    ntasks: int = field(default=1,
                        metadata=dict(help="Number of MPI processes. If greater than 1, it triggers mpirun."))
    # modules to be load
    modules: list = field(default_factory=list, metadata=dict(help="Modules to load"))
    # extra packages to install
    extra_packages: list = field(default_factory=list, metadata=dict(help="Extra packages to install"))

    _suites: FilePlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _experiments: FilePlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: FilePlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _assets: FilePlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)
    _metas: JSONMetadataOperations = field(**op_defaults, repr=False, init=False)
    _op_client: FileOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):
        self.__init_interfaces()
        self.supported_types = {ItemType.SUITE, ItemType.EXPERIMENT, ItemType.SIMULATION}
        if self.job_directory is None:
            raise ValueError("Job Directory is required.")
        self.job_directory = os.path.abspath(self.job_directory)
        self.name_directory = IdmConfigParser.get_option(None, "name_directory", 'True').lower() in TRUTHY_VALUES
        self.sim_name_directory = IdmConfigParser.get_option(None, "sim_name_directory",
                                                             'False').lower() in TRUTHY_VALUES
        super().__post_init__()
        self._object_cache_expiration = 600

    def __init_interfaces(self):
        self._suites = FilePlatformSuiteOperations(platform=self)
        self._experiments = FilePlatformExperimentOperations(platform=self)
        self._simulations = FilePlatformSimulationOperations(platform=self)
        self._assets = FilePlatformAssetCollectionOperations(platform=self)
        self._metas = JSONMetadataOperations(platform=self)
        self._op_client = FileOperations(platform=self)

    def post_setstate(self):
        """
        Utility function.
        Returns: None
        """
        self.__init_interfaces()

    def mk_directory(self, item: Union[Suite, Experiment, Simulation] = None, dest: Union[Path, str] = None,
                     exist_ok: bool = True) -> None:
        """
        Make a new directory.
        Args:
            item: Suite/Experiment/Simulation
            dest: the folder path
            exist_ok: True/False

        Returns:
            None
        """
        self._op_client.mk_directory(item, dest, exist_ok)

    def get_directory(self, item: Union[Suite, Experiment, Simulation]) -> Path:
        """
        Get item's path.
        Args:
            item: Suite, Experiment, Simulation
        Returns:
            item file directory
        """
        return self._op_client.get_directory(item)

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        """
        Get item's path.
        Args:
            item_id: entity id (Suite, Experiment, Simulation)
            item_type: the type of items (Suite, Experiment, Simulation)
        Returns:
            item file directory
        """
        return self._op_client.get_directory_by_id(item_id, item_type)

    def create_batch_file(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        self._op_client.create_batch_file(item, **kwargs)

    @staticmethod
    def update_script_mode(script_path: Union[Path, str], mode: int = 0o777) -> None:
        """
        Change file mode.
        Args:
            script_path: script path
            mode: permission mode
        Returns:
            None
        """
        script_path = Path(script_path)
        script_path.chmod(mode)

    def flatten_item(self, item: IEntity, raw=False, **kwargs) -> List[object]:
        """
        Flatten an item: resolve the children until getting to the leaves.

        For example, for an experiment, will return all the simulations.
        For a suite, will return all the simulations contained in the suites experiments.

        Args:
            item: Which item to flatten
            raw: bool
            kwargs: extra parameters

        Returns:
            List of leaves
        """
        if not raw:
            interface = ITEM_TYPE_TO_OBJECT_INTERFACE[item.item_type]
            idm_item = getattr(self, interface).to_entity(item)
            return super().flatten_item(idm_item)

        if isinstance(item, FileSuite):
            experiments = self._suites.get_children(item, parent=item, raw=True)
            children = list()
            for file_exp in experiments:
                children += self.flatten_item(item=file_exp, raw=raw)
        elif isinstance(item, FileExperiment):
            children = self._experiments.get_children(item, parent=item, raw=True)
            exp = Experiment()
            exp.uid = item.id
            exp.platform = self
            exp._platform_object = item
            exp.tags = item.tags

            for file_sim in children:
                file_sim.experiment = exp
                file_sim.platform = self
        elif isinstance(item, FileSimulation):
            if raw:
                children = [item]
            else:
                exp = Experiment()
                exp.uid = item.id
                exp.platform = self
                exp._platform_object = item
                exp.tags = item.tags
                sim = self._simulations.to_entity(item, parent=exp)
                sim.experiment = exp
                children = [sim]
        elif isinstance(item, Suite):
            file_suite = item.get_platform_object()
            file_suite.platform = self
            children = self.flatten_item(item=file_suite)
        elif isinstance(item, Experiment):
            children = item.simulations.items
        elif isinstance(item, Simulation):
            children = [item]
        else:
            raise Exception(f'Item Type: {type(item)} is not supported!')

        return children

    def validate_item_for_analysis(self, item: Union[Simulation, FileSimulation], analyze_failed_items=False):
        """
        Check if item is valid for analysis.

        Args:
            item: which item to verify status
            analyze_failed_items: bool

        Returns: bool
        """
        result = False

        # TODO: we may consolidate two cases into one
        if isinstance(item, FileSimulation):
            if item.status == EntityStatus.SUCCEEDED:
                result = True
            else:
                if analyze_failed_items and item.status == EntityStatus.FAILED:
                    result = True
        elif isinstance(item, Simulation):
            if item.succeeded:
                result = True
            else:
                if analyze_failed_items and item.status == EntityStatus.FAILED:
                    result = True
        return result

    def link_file(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link files.
        Args:
            target: the source file path
            link: the file path
        Returns:
            None
        """
        self._op_client.link_file(target, link)

    def link_dir(self, target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link directory/files.
        Args:
            target: the source folder path.
            link: the folder path
        Returns:
            None
        """
        self._op_client.link_dir(target, link)

    def make_command_executable(self, simulation: Simulation) -> None:
        """
        Make simulation command executable.
        Args:
            simulation: idmtools Simulation
        Returns:
            None
        """
        self._op_client.make_command_executable(simulation)

    def get_simulation_status(self, sim_id: str, **kwargs) -> EntityStatus:
        """
        Retrieve simulation status.
        Args:
            sim_id: Simulation ID
            kwargs: keyword arguments used to expand functionality
        Returns:
            EntityStatus
        """
        return self._op_client.get_simulation_status(sim_id, **kwargs)

    def entity_display_name(self, item: Union[Suite, Experiment, Simulation]) -> str:
        """
        Get display name for entity.
        Args:
            item: Suite, Experiment or Simulation
        Returns:
            str
        """
        return self._op_client.entity_display_name(item)
