from dataclasses import dataclass

from idmtools.entities import IExperiment
from tests.utils.TestSimulation import TestSimulation


@dataclass(repr=False)
class TestExperiment(IExperiment):
    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=TestSimulation)

    def gather_assets(self) -> None:
        pass
