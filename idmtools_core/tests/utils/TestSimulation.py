import json

from idmtools.assets import Asset
from idmtools.entities import ISimulation


class TestSimulation(ISimulation):
    def __init__(self):
        super().__init__()
        self.parameters = {}

    def set_parameter(self, name: str, value: any) -> dict:
        self.parameters[name] = value
        return {"name": value}

    def gather_assets(self) -> None:
        self.assets.add_asset(Asset("config.json", content=json.dumps(self.parameters)))
