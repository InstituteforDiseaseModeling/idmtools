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
    For example:
    ```python
        p = PythonSimulation(parameters={"a":1}, envelope="config")
    ```
    will allow you to access the parameters directly like:
    ```python
        p.parameters["a"] = 2
        # or
        p.set_parameter("a",2)
    ```
    but will generate the following config.json file:
    ```json
        { "config": {
          "a":2
          }
        }
    ```

    It is also possible to pass parameters already including an enveloppe:
    ```python
        p = PythonSimulation(parameters={"config":{"a":1}}, envelope="config")
    ```
    The access of the parameters will work the same:
    ``` python
         p.parameters["a"] = 2
        # or
        p.set_parameter("a",2)
    ```
    And the generation will work as expected, including the envelope:
    ```json
        { "config": {
          "a":2
          }
        }
    ```
    """
    parameters: dict = field(default_factory=lambda:{})
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

    def gather_assets(self) -> None:
        params = {self.envelope:self.parameters} if self.envelope else self.parameters
        self.assets.add_asset(Asset(filename="config.json", content=json.dumps(params)))
