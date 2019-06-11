import json

from idmtools.assets import Asset
from idmtools.entities import ISimulation


class PythonSimulation(ISimulation):
    def __init__(self, parameters=None, assets=None):
        super().__init__(assets=assets)
        self.parameters = parameters or {"parameters": {}}

    def set_parameter(self, name: str, value: any) -> dict:
        self.parameters["parameters"][name] = value
        return {name: value}

    def gather_assets(self) -> None:
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(self.parameters)))

