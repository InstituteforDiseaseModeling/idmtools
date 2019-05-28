import json

from assets.Asset import Asset
from interfaces.IEntity import IEntity


class ISimulation(IEntity):
    """
    Represents a generic Simulation.
    This class needs to be implemented for each model type with specifics.
    """

    def __init__(self, parameters=None, assets=None):
        super().__init__(assets=assets)
        self.parameters = parameters or {"parameters":{}}
        self.experiment_id = None

    def set_parameter(self, name:str, value:any) -> dict:
        self.parameters["parameters"][name] = value
        return {name: value}

    def __repr__(self):
        return f"<Simulation: {self.uid} - Exp_id: {self.experiment_id}>"

    def gather_assets(self):
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(self.parameters)))