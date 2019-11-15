from abc import ABCMeta
from typing import Dict


class IEMODDefault(metaclass=ABCMeta):
    def config(self) -> Dict:
        return {}

    def campaign(self) -> Dict:
        return {}

    def demographics(self) -> Dict:
        return {}

    def process_simulation(self, simulation):
        simulation.campaign = self.campaign()

        simulation.config = self.config()
