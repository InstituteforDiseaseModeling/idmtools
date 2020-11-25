import copy
import logging
import os
import sys
from dataclasses import dataclass, field
from os import PathLike
from pathlib import PurePath
from typing import List, Union
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools_platform_file._api.asset_collection_operations import FilePlatformAssetCollectionOperations
from idmtools_platform_file._api.experiment_operations import FilePlatformExperimentOperations
from idmtools_platform_file._api.simulation_operations import FilePlatformSimulationOperations
from idmtools_platform_file._api.suite_operations import FilePlatformSuiteOperations
from idmtools_platform_file._api.workitem_operations import FilePlatformWorkflowItemOperations

logger = logging.getLogger(__name__)
supported_types = [PlatformRequirements.PYTHON, PlatformRequirements.SHELL, PlatformRequirements.NativeBinary]
op_defaults = dict(default=None, compare=False, metadata=dict(pickle_ignore=True))


def get_default_template(platform: str = None):
    if platform is None:
        platform = "linux"
    with open(PurePath(__file__).parent.joinpath(f"{platform.lower()}_simulation_script_template.sh.jinja2"), 'r') as sin:
        return sin.read()


@dataclass(repr=False)
class FilePlatform(IPlatform):
    #: Base path to write output to
    output_directory: Union[str, PathLike] = field(default=None)
    #: Use name for directories of work items and experiments
    experiment_prefix_str: str = field(default='{item.name}{i}')
    #: Should softlinks be used when copying files?
    use_links: bool = field(default=False)
    #: Use name for simulations directories
    simulation_prefix_str: str = field(default='{i}')
    #: Should we write out scripts
    write_scripts: bool = field(default=False)
    #: Simulation Template
    simulation_exec_template: str = field(default_factory=get_default_template)
    #: copy_experiment_assets
    copy_experiment_assets: bool = field(default=False)

    #: Should we also produce metadata files?
    add_metadata: bool = field(default=True)

    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types), repr=False, init=False)
    _experiments: FilePlatformExperimentOperations = field(**op_defaults, repr=False, init=False)
    _simulations: FilePlatformSimulationOperations = field(**op_defaults, repr=False, init=False)
    _suites: FilePlatformSuiteOperations = field(**op_defaults, repr=False, init=False)
    _workflow_items: FilePlatformWorkflowItemOperations = field(**op_defaults, repr=False, init=False)
    _assets: FilePlatformAssetCollectionOperations = field(**op_defaults, repr=False, init=False)

    def __post_init__(self):

        if isinstance(self.output_directory, PathLike):
            self.output_directory = str(self.output_directory)
        if self.use_links and sys.platform in ["win32"]:
            raise ValueError("Links are not supported on Windows")
        if not self.output_directory:
            raise ValueError("Output directory is required")
        elif not os.path.exists(self.output_directory):
            logger.debug(f"Creating File platform output: {self.output_directory}")
            os.makedirs(self.output_directory)
        elif os.path.isfile(self.output_directory):
            raise ValueError("Output directory cannot be a file.")
        self.__init_interfaces()
        super().__post_init__()

    def __init_interfaces(self):
        self._experiments = FilePlatformExperimentOperations(platform=self)
        self._simulations = FilePlatformSimulationOperations(platform=self)
        self._suites = FilePlatformSuiteOperations(platform=self)
        self._workflow_items = FilePlatformWorkflowItemOperations(platform=self)
        self._assets = FilePlatformAssetCollectionOperations(platform=self)

    def post_setstate(self):
        self.__init_interfaces()
