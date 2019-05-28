import json

from assets.Asset import Asset
from assets.AssetCollection import AssetCollection
from entities.IEntity import IEntity


class ISimulation(IEntity):
    """
    Represents a generic Simulation.
    This class needs to be implemented for each model type with specifics.
    """

    def __init__(self, parameters: dict = None, assets: AssetCollection = None, experiment: IEntity = None):
        super().__init__()
        self.assets = assets or AssetCollection()
        self.parameters = parameters or {"parameters": {}}
        self.experiment = experiment

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
        return f"<Simulation: {self.uid} - Exp_id: {self.experiment_id}>"

    def gather_assets(self):
        """
        Gather all the assets for the simulation.
        By default, only create a config.json containing the parameters
        """
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(self.parameters)))
