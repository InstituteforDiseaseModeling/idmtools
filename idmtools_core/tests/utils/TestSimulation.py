import json
from dataclasses import dataclass, field

from idmtools.assets import Asset
from idmtools.entities import ISimulation


@dataclass(repr=False)
class TestSimulation(ISimulation):
    parameters: dict = field(default_factory=lambda: {})

    def set_parameter(self, name: str, value: any) -> dict:
        self.parameters[name] = value
        return {"name": value}

    def gather_assets(self) -> None:
        self.assets.add_asset(Asset("config.json", content=json.dumps(self.parameters)))
