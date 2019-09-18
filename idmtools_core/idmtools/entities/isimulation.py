import typing
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field

from idmtools.entities.iroot_item import IRootItem
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment


@dataclass
class ISimulation(IAssetsEnabled, IRootItem, metaclass=ABCMeta):
    """
    Represents a generic Simulation.
    This class needs to be implemented for each model type with specifics.
    """
    experiment: 'TExperiment' = field(default=None, compare=False, metadata={"md": True})

    @abstractmethod
    def set_parameter(self, name: str, value: any) -> dict:
        """
        Set a parameter in the simulation
        Args:
            name: Name of the parameter
            value: Value of the parameter
        Returns: Tag to record the change
        """
        pass

    @abstractmethod
    def get_parameter(self, name, default=None):
        """
        Get a parameter in the simulation
        Args:
            name: Name of the parameter
        Returns: the Value of the parameter
        """
        return None

    @abstractmethod
    def update_parameters(self, params):
        """
        Bulk update parameters/config
        Args:
            params: dict with new values
        Returns: None
        """
        pass

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.experiment.uid if self.experiment else None}>"

    def pre_creation(self):
        self.gather_assets()

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
