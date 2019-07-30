import json
from dataclasses import dataclass, field
from idmtools.assets import Asset
from idmtools.entities import ISimulation
from idmtools_models.dtk.interventions.DTKEmptyCampaign import DTKEmptyCampaign


@dataclass(repr=False)
class DTKSimulation(ISimulation):
    config: dict = field(default_factory=lambda: {})
    campaign: dict = field(default_factory=lambda: DTKEmptyCampaign.campaign())
    demographics: dict = field(default_factory=lambda: {})

    def set_parameter(self, name: str, value: any) -> dict:
        self.config[name] = value
        return {name: value}

    def get_parameter(self, name, default=None):
        """
        Get a parameter in the simulation
        Args:
            name: Name of the parameter
        Returns: the Value of the parameter
        """
        return self.config.get(name, default)

    def update_parameters(self, params):
        """
        Bulk update config
        Args:
            params: dict with new values
        Returns: None
        """
        self.config.update(params)

    def gather_assets(self):
        config = {"parameters": self.config}
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(config)), fail_on_duplicate=False)
        self.assets.add_asset(Asset(filename="campaign.json", content=json.dumps(self.campaign)),
                              fail_on_duplicate=False)
        for filename, content in self.demographics.items():
            self.assets.add_asset(Asset(filename=filename, content=json.dumps(content)), fail_on_duplicate=False)

    def load_files(self, config_path=None, campaign_path=None, demographics_path=None, force=False):
        """
        Provide a way to load custom files
        Args:
            config_path: custom config file
            campaign_path: custom campaign file
            demographics_path: custom demographics file
            force: always return if True, else throw exception is something wrong
        Returns: None
        """
        import json

        def load_file(file_path):
            try:
                with open(file_path, 'rb') as f:
                    return json.load(f)
            except IOError:
                if not force:
                    raise Exception(f"Encounter issue when loading file: {file_path}")
                else:
                    return None

        if config_path:
            jn = load_file(config_path)
            if jn:
                self.config = jn

        if campaign_path:
            jn = load_file(campaign_path)
            if jn:
                self.campaign = jn

        if demographics_path:
            jn = load_file(demographics_path)
            if jn:
                self.demographics = jn
