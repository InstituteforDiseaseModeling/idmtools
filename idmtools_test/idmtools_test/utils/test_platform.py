import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import Dict, List, Type, NoReturn
from idmtools.entities.iplatform import IPlatformIOOperations
from idmtools.core import ItemType
from idmtools.core.interfaces.iitem import IItem
from idmtools.entities import IPlatform
from idmtools.entities.iexperiment import IExperiment, ILinuxExperiment, IWindowsExperiment, \
    IGPUExperiment, IDockerExperiment
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_test.utils.test_platform_commissioning import TestPlatformCommissioningOperations
from idmtools_test.utils.test_platform_metadata import TestPlatformMetadataOperations


logger = getLogger(__name__)


class TestPlatformIOOperations(IPlatformIOOperations):
    parent: 'TestPlatform'

    def send_assets(self, item: IItem, **kwargs) -> NoReturn:
        logger.debug(f'Test Platform send assets called for {item.uid}')
        pass

    def get_files(self, item: IItem, files: List[str]) -> Dict[str, bytearray]:
        logger.debug(f'Test Platform get files called for {item.uid}')
        return {}


@dataclass(repr=False)
class TestPlatform(IPlatform):
    """
    Test platform simulating a working platform to use in the test suites.
    """

    commissioning: TestPlatformCommissioningOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})
    io: TestPlatformIOOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})
    metadata: TestPlatformMetadataOperations = field(default=None, compare=False, metadata={"pickle_ignore": True})

    __test__ = False  # Hide from test discovery

    def __post_init__(self):
        self.init_interfaces()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION}
        super().__post_init__()

    def init_interfaces(self):
        self.commissioning = TestPlatformCommissioningOperations(self)
        self.io = TestPlatformIOOperations(self)
        self.metadata = TestPlatformMetadataOperations(self)

    def supported_experiment_types(self) -> List[Type]:
        os_ex = IWindowsExperiment if os.name == "nt" else ILinuxExperiment
        return [IExperiment, os_ex]

    def unsupported_experiment_types(self) -> List[Type]:
        os_ex = IWindowsExperiment if os.name != "nt" else ILinuxExperiment
        return [IGPUExperiment, IDockerExperiment, os_ex]

    def post_setstate(self):
        self.init_interfaces()
        self.metadata.initialize_test_cache()

    def run_simulations(self, experiment: IExperiment) -> None:
        from idmtools.core import EntityStatus
        self.metadata.set_simulation_status(experiment.uid, EntityStatus.RUNNING)


TEST_PLATFORM_EXAMPLE_CONFIG = """
[Test]

"""


class TestPlatformSpecification(PlatformSpecification):

    @get_description_impl
    def get_description(self) -> str:
        return "Provides access to the Test Platform to IDM Tools"

    @get_platform_impl
    def get(self, **configuration) -> IPlatform:
        """
        Build our test platform from the passed in configuration object

        We do our import of platform here to avoid any weir
        Args:
            configuration:

        Returns:

        """
        return TestPlatform(**configuration)

    @example_configuration_impl
    def example_configuration(self):
        return TEST_PLATFORM_EXAMPLE_CONFIG

    @get_platform_type_impl
    def get_type(self) -> Type[TestPlatform]:
        return TestPlatform
