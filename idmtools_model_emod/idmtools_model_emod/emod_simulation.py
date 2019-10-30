import json
from dataclasses import dataclass, field
from typing import Optional, Any

from idmtools.assets import Asset
from idmtools.entities import ISimulation
from idmtools_model_emod.emod_file import DemographicsFiles
from idmtools_model_emod.interventions import EMODEmptyCampaign


@dataclass(repr=False)
class EMODSimulation(ISimulation):
    config: dict = field(default_factory=lambda: {})
    campaign: dict = field(default_factory=lambda: EMODEmptyCampaign.campaign())
    demographics: DemographicsFiles = field(default_factory=lambda: DemographicsFiles())

    def set_parameter(self, name: str, value: any) -> dict:
        self.config[name] = value
        return {name: value}

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
        super().pre_creation()

    def gather_assets(self):
        config = {"parameters": self.config}

        # Add config and campaign to assets
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(config)), fail_on_duplicate=False)
        self.assets.add_asset(Asset(filename="campaign.json", content=json.dumps(self.campaign)),
                              fail_on_duplicate=False)

        # Add demographics files to assets
        self.assets.extend(self.demographics.gather_assets())

    def __hash__(self):
        return id(self.uid)
