import typing
from abc import ABC, abstractmethod

from idmtools.core import EntityStatus, IAssetsEnabled, IEntity

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment
    from idmtools.assets import AssetCollection


class ISimulation(IAssetsEnabled, IEntity, ABC):
    """
    Represents a generic Simulation.
    This class needs to be implemented for each model type with specifics.
    """
    pickle_ignore_fields = ["assets"]

    def __init__(self, assets: 'AssetCollection' = None, experiment: 'TExperiment' = None):
        IAssetsEnabled.__init__(self, assets=assets)
        IEntity.__init__(self)

        self.experiment = experiment
        self.status = None

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

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.experiment.uid}>"

    def pre_creation(self):
        self.gather_assets()

    @abstractmethod
    def gather_assets(self):
        """
        Gather all the assets for the simulation.
        """
        pass

    @property
    def done(self):
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self):
        return self.status == EntityStatus.SUCCEEDED

