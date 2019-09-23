from abc import ABCMeta
from typing import Dict

from idmtools.utils.decorators import abstractstatic


class IDTKDefault(metaclass=ABCMeta):
    @abstractstatic
    def config() -> Dict:
        return {}

    @abstractstatic
    def campaign() -> Dict:
        return {}

    @abstractstatic
    def demographics() -> Dict:
        return {}

    @classmethod
    def process_simulation(cls, simulation):
        if cls.campaign:
            simulation.campaign = cls.campaign()

        if cls.config:
            simulation.config = cls.config()

        # # The default demographics will be added to Experiment instead
        # if cls.demographics:
        #     simulation.demographics = cls.demographics()
