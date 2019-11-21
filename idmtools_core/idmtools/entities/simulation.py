import typing
from abc import ABCMeta
from dataclasses import dataclass, field
from idmtools.core import ItemType
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.imodel import IModel


@dataclass
class Simulation(INamedEntity, metaclass=ABCMeta):
    """
    Class that represents a generic simulation.
    This class needs to be implemented for each model type with specifics.
    """
    item_type: 'ItemType' = field(default=ItemType.SIMULATION, compare=False)
    model: IModel = field(default=None)

    @property
    def experiment(self):
        return self.parent

    @property
    def assets(self):
        return self.model.assets

    @experiment.setter
    def experiment(self, experiment):
        self.parent = experiment

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.parent_id}>"

    def __hash__(self):
        return id(self.uid)

    def set_parameter(self, *args, **kwargs):
        return self.model.set_parameter(*args, **kwargs)

    def get_parameter(self, *args, **kwargs):
        return self.model.get_parameter(*args, **kwargs)

    def pre_creation(self):
        self.model.pre_simulation_creation()
        self.gather_assets()

    def pre_getstate(self):
        """
        Return default values for :meth:`pickle_ignore_fields`. Call before pickling.
        """
        from idmtools.assets import AssetCollection
        from idmtools.core.interfaces.entity_container import EntityContainer
        return {"assets": AssetCollection(), "simulations": EntityContainer()}

    def gather_assets(self):
        """
        Gather all the assets for the simulation.
        """
        self.model.gather_assets()


TSimulation = typing.TypeVar("TSimulation", bound=Simulation)
TSimulationClass = typing.Type[TSimulation]
TSimulationBatch = typing.List[TSimulation]
TAllSimulationData = typing.Mapping[TSimulation, typing.Any]
TSimulationList = typing.List[typing.Union[TSimulation, str]]


@dataclass(repr=False)
class StandardSimulation(Simulation):
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
