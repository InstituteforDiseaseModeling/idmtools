import json
from dataclasses import dataclass, field

from idmtools.assets import Asset
from idmtools.entities import ISimulation


@dataclass(repr=False)
class TestSimulation(ISimulation):
    parameters: dict = field(default_factory=lambda: {})
    status: 'EntityStatus' = field(default=None, compare=False, metadata={"pickle_ignore": False})

    def set_parameter(self, name: str, value: any) -> dict:
        self.parameters[name] = value
        return {"name": value}

    def get_parameter(self, name, default=None):
        """
        Get a parameter in the simulation
        Args:
            name: Name of the parameter
        Returns: the Value of the parameter
        """
        return self.parameters.get(name, default)

    def update_parameters(self, params):
        """
        Bulk update parameters
        Args:
            params: dict with new values
        Returns: None
        """
        self.parameters.update(params)

    def gather_assets(self) -> None:
        self.assets.add_asset(Asset("config.json", content=json.dumps(self.parameters)))
