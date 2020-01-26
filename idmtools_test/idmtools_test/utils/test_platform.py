import copy
import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import List, Type

from idmtools.core import ItemType
from idmtools.entities.iexperiment import IExperiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.registry.platform_specification import example_configuration_impl, get_platform_impl, \
    get_platform_type_impl, PlatformSpecification
from idmtools.registry.plugin_specification import get_description_impl
from idmtools_test.utils.operations.experiment_operations import TestPlaformExperimentOperation
from idmtools_test.utils.operations.simulation_operations import TestPlaformSimulationOperation

logger = getLogger(__name__)
current_directory = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.abspath(os.path.join(current_directory, "..", "data"))

supported_types = [PlatformRequirements.SHELL, PlatformRequirements.NativeBinary, PlatformRequirements.PYTHON,
                   PlatformRequirements.WINDOWS if os.name == "nt" else PlatformRequirements.LINUX]


@dataclass(repr=False)
class TestPlatform(IPlatform):
    """
    Test platform simulating a working platform to use in the test suites.
    """

    _experiments: TestPlaformExperimentOperation = field(default=None, compare=False, metadata={"pickle_ignore": True})
    _simulations: TestPlaformSimulationOperation = field(default=None, compare=False, metadata={"pickle_ignore": True})

    _platform_supports: List[PlatformRequirements] = field(default_factory=lambda: copy.deepcopy(supported_types))

    __test__ = False  # Hide from test discovery

    def __post_init__(self):
        self.init_interfaces()
        self.supported_types = {ItemType.EXPERIMENT, ItemType.SIMULATION}
        super().__post_init__()

    def init_interfaces(self):
        self._experiments = TestPlaformExperimentOperation(self)
        self._simulations = TestPlaformSimulationOperation(self)

    def post_setstate(self):
        self.init_interfaces()

    def run_simulations(self, experiment: IExperiment) -> None:
        from idmtools.core import EntityStatus
        self._simulations.set_simulation_status(experiment.uid, EntityStatus.RUNNING)

    def cleanup(self):
        self._experiments.experiments = dict()
        self._simulations.simulations = dict()


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
