import json
import typing
from abc import ABC

from idmtools.assets import Asset, AssetCollection
from idmtools.core import EntityStatus, IAssetsEnabled, IEntity

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment


class ISimulation(IAssetsEnabled, IEntity, ABC):
    """
    Represents a generic Simulation.
    This class needs to be implemented for each model type with specifics.
    """

    def __init__(self, parameters: dict = None, assets: 'AssetCollection' = None, experiment: 'TExperiment' = None):
        IAssetsEnabled.__init__(self, assets)
        IEntity.__init__(self)
        self.assets = assets or AssetCollection()
        self.parameters = parameters or {"parameters": {}}
        self.experiment = experiment
        self.status = None

    def set_parameter(self, name: str, value: any) -> dict:
        """
        Set a parameter in the simulation
        Args:
            name: Name of the parameter
            value: Value of the parameter

        Returns: Tag to record the change
        """
        self.parameters["parameters"][name] = value
        return {name: value}

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.experiment.uid}>"

    def pre_creation(self):
        self.gather_assets()

    def gather_assets(self):
        """
        Gather all the assets for the simulation.
        By default, only create a config.json containing the parameters
        """
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(self.parameters)))

    @property
    def done(self):
        return self.status in (EntityStatus.SUCCEEDED, EntityStatus.FAILED)

    @property
    def succeeded(self):
        return self.status == EntityStatus.SUCCEEDED
