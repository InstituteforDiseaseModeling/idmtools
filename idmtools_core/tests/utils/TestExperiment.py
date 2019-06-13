from idmtools.entities import IExperiment
from tests.utils.TestSimulation import TestSimulation


class TestExperiment(IExperiment):
    def __init__(self, name):
        super().__init__(name, simulation_type=TestSimulation)

    def gather_assets(self) -> None:
        pass