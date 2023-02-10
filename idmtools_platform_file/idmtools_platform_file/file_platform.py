from dataclasses import dataclass, field
from pathlib import Path
from typing import Union

from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.simulation import Simulation
from idmtools_platform_file.assets import generate_script, generate_simulation_script
from idmtools_platform_file.platform_operations.asset_collection_operations import FilePlatformAssetCollectionOperations
from idmtools_platform_file.platform_operations.experiment_operations import FilePlatformExperimentOperations
from idmtools_platform_file.platform_operations.json_metadata_operations import JSONMetadataOperations
from idmtools_platform_file.platform_operations.simulation_operations import FilePlatformSimulationOperations
from idmtools_platform_file.platform_operations.suite_operations import FilePlatformSuiteOperations

op_defaults = dict(default=None, compare=False, metadata={"pickle_ignore": True})


@dataclass(repr=False)
class FilePlatform(IPlatform):
    job_directory: str = field(default=None)

    # Default retries for jobs
    retries: int = field(default=1, metadata=dict(sbatch=False))

    _suites: FilePlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _experiments: FilePlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: FilePlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _assets: FilePlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)

    _metas: JSONMetadataOperations = field(**op_defaults, repr=False, init=False)

    # Which batch script to use by default
    batch_template: str = field(default="batch.sh.jinja2")

    simulation_template: str = field(default="_run.sh.jinja2")

    def __post_init__(self):
        self.__init_interfaces()
        self.supported_types = {ItemType.SUITE, ItemType.EXPERIMENT, ItemType.SIMULATION}
        if self.job_directory is None:
            raise ValueError("Job Directory is required.")
        super().__post_init__()

    def __init_interfaces(self):
        self._suites = FilePlatformSuiteOperations(platform=self)
        self._experiments = FilePlatformExperimentOperations(platform=self)
        self._simulations = FilePlatformSimulationOperations(platform=self)
        self._assets = FilePlatformAssetCollectionOperations(platform=self)
        self._metas = JSONMetadataOperations(platform=self)

    def post_setstate(self):
        self.__init_interfaces()

    def get_directory(self, item: Union[Suite, Experiment, Simulation]) -> Path:
        """
        Get item's path.
        Args:
            item: Suite, Experiment, Simulation
        Returns:
            item file directory
        """
        if isinstance(item, Suite):
            item_dir = Path(self.job_directory, item.id)
        elif isinstance(item, Experiment):
            suite_id = item.parent_id or item.suite_id
            if suite_id is None:
                raise RuntimeError("Experiment missing parent!")
            suite_dir = Path(self.job_directory, str(suite_id))
            item_dir = Path(suite_dir, item.id)
        elif isinstance(item, Simulation):
            exp = item.parent
            if exp is None:
                raise RuntimeError("Simulation missing parent!")
            exp_dir = self.get_directory(exp)
            item_dir = Path(exp_dir, item.id)
        else:
            raise RuntimeError(f"Get directory is not supported for {type(item)} object on FilePlatform")

        return item_dir

    def get_directory_by_id(self, item_id: str, item_type: ItemType) -> Path:
        """
        Get item's path.
        Args:
            item_id: entity id (Suite, Experiment, Simulation)
            item_type: the type of items (Suite, Experiment, Simulation)
        Returns:
            item file directory
        """
        if item_type is ItemType.SIMULATION:
            pattern = f"*/*/{item_id}"
        elif item_type is ItemType.EXPERIMENT:
            pattern = f"*/{item_id}"
        elif item_type is ItemType.SUITE:
            pattern = f"{item_id}"
        else:
            raise RuntimeError(f"Unknown item type: {item_type}")

        root = Path(self.job_directory)
        for item_path in root.glob(pattern=pattern):
            return item_path
        raise RuntimeError(f"Not found path for item_id: {item_id} with type: {item_type}.")

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
        if dest is not None:
            target = Path(dest)
        elif isinstance(item, (Suite, Experiment, Simulation)):
            target = self.get_directory(item)
        else:
            raise RuntimeError('Only support Suite/Experiment/Simulation or not None dest.')
        target.mkdir(parents=True, exist_ok=exist_ok)

    @staticmethod
    def link_file(target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link files.
        Args:
            target: the source file path
            link: the file path
        Returns:
            None
        """
        target = Path(target).absolute()
        link = Path(link).absolute()
        link.symlink_to(target)

    @staticmethod
    def link_dir(target: Union[Path, str], link: Union[Path, str]) -> None:
        """
        Link directory/files.
        Args:
            target: the source folder path.
            link: the folder path
        Returns:
            None
        """
        target = Path(target).absolute()
        link = Path(link).absolute()
        link.symlink_to(target)

    def create_batch_file(self, item: Union[Experiment, Simulation], **kwargs) -> None:
        """
        Create batch file.
        Args:
            item: the item to build batch file for
            kwargs: keyword arguments used to expand functionality.
        Returns:
            None
        """
        if isinstance(item, Experiment):
            generate_script(self, item, template=self.batch_template)
        elif isinstance(item, Simulation):
            retries = kwargs.get('retries', None)
            generate_simulation_script(self, item, retries, template=self.simulation_template)
        else:
            raise NotImplementedError(f"{item.__class__.__name__} is not supported for batch creation.")
