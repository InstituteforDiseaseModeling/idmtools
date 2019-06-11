from abc import ABCMeta
from typing import Dict


class IDTKDefault(metaclass=ABCMeta):
    @property
    def config(self) -> Dict:
        return {}

    @property
    def campaign(self) -> Dict:
        return {}

    @property
    def demographics(self) -> Dict:
        return {}

    def process_simulation(self, simulation):
        if self.campaign:
            simulation.campaign = self.campaign

        if self.config:
            simulation.config = self.config

        if self.demographics:
            simulation.demographics = self.demographics
