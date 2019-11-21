from abc import ABC, abstractmethod
from dataclasses import dataclass
from idmtools.entities.itask import ITask


@dataclass
class IModel(ITask, ABC):
    @abstractmethod
    def gather_experiment_assets(self):
        pass

    @abstractmethod
    def pre_experiment_creation(self):
        pass

    @abstractmethod
    def pre_simulation_creation(self):
        pass

    @abstractmethod
    def set_parameter(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_parameter(self, *args, **kwargs):
        pass