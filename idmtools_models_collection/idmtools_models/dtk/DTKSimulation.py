import json

from idmtools.assets import Asset
from idmtools.entities import ISimulation
from idmtools_models.dtk.interventions.DTKEmptyCampaign import DTKEmptyCampaign


class DTKSimulation(ISimulation):
    def __init__(self, config=None, campaign=None, demographics=None):
        super().__init__()
        self.config = config
        self.demographics = demographics or {}
        self.campaign = campaign or DTKEmptyCampaign.campaign

    def set_parameter(self, name: str, value: any) -> dict:
        self.config[name] = value
        return {name: value}

    def gather_assets(self):
        config = {"parameters": self.config}
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(config)))
        self.assets.add_asset(Asset(filename="campaign.json", content=json.dumps(self.campaign)))
        for filename, content in self.demographics.items():
            self.assets.add_asset(Asset(filename=filename, content=json.dumps(content)))
