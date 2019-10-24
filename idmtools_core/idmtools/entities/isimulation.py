import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from idmtools.core import ItemType
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity


@dataclass
class ISimulation(IAssetsEnabled, INamedEntity, metaclass=ABCMeta):
    """
    Class that represents a generic simulation.
    This class needs to be implemented for each model type with specifics.
    """
    item_type: 'ItemType' = field(default=ItemType.SIMULATION, compare=False)

    @property
    def experiment(self):
        return self.parent

    @experiment.setter
    def experiment(self, experiment):
        self.parent = experiment

    @abstractmethod
    def set_parameter(self, name: str, value: any) -> dict:
        """
        Set a parameter in the simulation.

        Args:
            name: The name of the parameter.
            value: The value of the parameter.

        Returns:    
            Tag to record the change.
        """
        pass

    @abstractmethod
    def get_parameter(self, name, default=None):
        """
        Get a parameter in the simulation.

        Args:
            name: The name of the parameter.

        Returns: 
            The value of the parameter.
        """
        return None

    @abstractmethod
    def update_parameters(self, params):
        """
        Bulk update parameter configuration.

        Args:
            params: A dictionary with new values.

        Returns: 
            None
        """
        pass

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.parent_id}>"

    def __hash__(self):
        return id(self.uid)

    def pre_creation(self):
        self.gather_assets()

    def pre_getstate(self):
        """
        Return default values for :meth:`pickle_ignore_fields`. Call before pickling.
        """
        from idmtools.assets import AssetCollection
        from idmtools.core.interfaces.entity_container import EntityContainer
        return {"assets": AssetCollection(), "simulations": EntityContainer()}

    @abstractmethod
    def gather_assets(self):
        """
        Gather all the assets for the simulation.
        """
        pass


TSimulation = typing.TypeVar("TSimulation", bound=ISimulation)
TSimulationClass = typing.Type[TSimulation]
TSimulationBatch = typing.List[TSimulation]
TAllSimulationData = typing.Mapping[TSimulation, typing.Any]
TSimulationList = typing.List[typing.Union[TSimulation, str]]


@dataclass(repr=False)
class StandardSimulation(ISimulation):
    def set_parameter(self, name: str, value: any) -> dict:
        pass

    def get_parameter(self, name, default=None):
        pass

    def update_parameters(self, params):
        pass

    def gather_assets(self):
        pass

    def __hash__(self):
        return id(self.uid)

