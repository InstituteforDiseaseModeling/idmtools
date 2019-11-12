import json
from dataclasses import dataclass, field
from typing import Optional, Any, NoReturn

from idmtools.assets import Asset
from idmtools.entities import ISimulation
from idmtools.utils.json import load_json_file
from idmtools_model_emod.emod_file import DemographicsFiles, MigrationFiles
from idmtools_model_emod.interventions import EMODEmptyCampaign


@dataclass(repr=False)
class EMODSimulation(ISimulation):
    config: dict = field(default_factory=lambda: {})
    campaign: dict = field(default_factory=lambda: EMODEmptyCampaign.campaign())
    demographics: DemographicsFiles = field(default_factory=lambda: DemographicsFiles())
    migrations: 'MigrationFiles' = field(default_factory=lambda: MigrationFiles())

    def set_parameter(self, name: str, value: any) -> dict:
        self.config[name] = value
        return {name: value}

    def load_files(self, config_path=None, campaign_path=None) -> 'NoReturn':
        """
        Load files in the experiment/base_simulation.

        Args:
            config_path: Configuration file path
            campaign_path: Campaign file path

        """
        if config_path:
            self.config = load_json_file(config_path)["parameters"]

        if campaign_path:
            self.campaign = load_json_file(campaign_path)

    def get_parameter(self, name: str, default: Optional[Any] = None):
        """
        Get a parameter in the simulation.

        Args:
            name: The name of the parameter.
            default: Optional, the default value.

        Returns: 
            The value of the parameter.
        """
        return self.config.get(name, default)

    def update_parameters(self, params):
        """
        Bulk update the configuration parameter values.

        Args:
            params: A dictionary with new values.

        Returns: 
            None
        """
        self.config.update(params)

    def pre_creation(self):
        # Set the demographics
        self.demographics.set_simulation_config(self)

        # Set the migrations
        self.migrations.set_simulation_config(self)

        super().pre_creation()

    def gather_assets(self):
        config = {"parameters": self.config}

        # Add config and campaign to assets
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(config, sort_keys=True)),
                              fail_on_duplicate=False)
        self.assets.add_asset(Asset(filename="campaign.json", content=json.dumps(self.campaign)),
                              fail_on_duplicate=False)

        # Add demographics files to assets
        self.assets.extend(self.demographics.gather_assets())

        # Add the migrations
        self.assets.extend(self.migrations.gather_assets())

    def __hash__(self):
        return id(self.uid)
