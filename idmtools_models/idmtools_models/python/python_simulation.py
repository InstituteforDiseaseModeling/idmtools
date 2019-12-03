import json
from dataclasses import dataclass, field

from idmtools.assets import Asset
from idmtools.entities import ISimulation


@dataclass(repr=False)
class PythonSimulation(ISimulation):
    """
    Represents a Python Simulation.
    This type of simulations have parameters and an eventual envelope.

    The envelope is just the name of the key wrapping the parameters.
    For example::

        p = PythonSimulation(parameters={"a":1}, envelope="config")

    will allow you to access the parameters directly like::

        p.parameters["a"] = 2
        # or
        p.set_parameter("a",2)

    but will generate the following config.json file::

        { "config": {
          "a":2
          }
        }


    It is also possible to pass parameters already including an envelope::

        p = PythonSimulation(parameters={"config":{"a":1}}, envelope="config")

    The access of the parameters will work the same::

        p.parameters["a"] = 2
        # or
        p.set_parameter("a",2)

    And the generation will work as expected, including the envelope::

        { "config": {
          "a":2
          }
        }

    """
    parameters: dict = field(default_factory=lambda: {})
    envelope: str = field(default=None)

    def __post_init__(self):
        super().__post_init__()

        # Process the envelope
        if self.envelope:
            if self.envelope in self.parameters.keys():
                self.parameters = self.parameters[self.envelope]

    def set_parameter(self, name: str, value: any) -> dict:
        self.parameters[name] = value
        return {name: value}

    def get_parameter(self, name, default=None):
        """
        Get a parameter in the simulation
        Args:
            name: Name of the parameter
        Returns:the Value of the parameter
        """
        return self.parameters.get(name, default)

    def update_parameters(self, params):
        """
        Bulk update parameters
        Args:
            params: dict with new values
        Returns:None
        """
        self.parameters.update(params)

    def gather_assets(self) -> None:
        params = {self.envelope: self.parameters} if self.envelope else self.parameters
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(params)), fail_on_duplicate=False)

    def __hash__(self):
        return id(self.uid)
