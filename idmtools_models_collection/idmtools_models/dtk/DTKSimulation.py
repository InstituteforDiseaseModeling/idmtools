import json
from dataclasses import dataclass, field

from idmtools.assets import Asset
from idmtools.entities import ISimulation
from idmtools_models.dtk.interventions.DTKEmptyCampaign import DTKEmptyCampaign


@dataclass
class DTKSimulation(ISimulation):
    config: dict = field(default_factory=lambda: {})
    campaign: dict = field(default_factory=lambda: DTKEmptyCampaign.campaign())
    demographics: dict = field(default_factory=lambda: {})

    def set_parameter(self, name: str, value: any) -> dict:
        self.config[name] = value
        return {name: value}

    def gather_assets(self):
        config = {"parameters": self.config}
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(config)))
        self.assets.add_asset(Asset(filename="campaign.json", content=json.dumps(self.campaign)))
        for filename, content in self.demographics.items():
            self.assets.add_asset(Asset(filename=filename, content=json.dumps(content)))
