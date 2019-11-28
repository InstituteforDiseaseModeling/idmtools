import json
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import Union, Dict, Any
from idmtools.assets import Asset
from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification

TJSONConfigKeyType = Union[str, int, float]
TJSONConfigValueType = Union[str, int, float, Dict[TJSONConfigKeyType, Any]]

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class JSONConfiguredTask(ITask):
    """
    Defines an extensible simple task that implements functionality through optional supplied use hooks
    """

    parameters: dict = field(default_factory=lambda: {})
    envelope: str = field(default=None)
    config_file_name: str = field(default="config.json")

    def gather_assets(self):
        """
        Here we dump our config
        """
        if logger.isEnabledFor(DEBUG):
            logger.info(f'Generating {self.config_file_name} as an asset from JSONConfiguredTask')
        params = {self.envelope: self.parameters} if self.envelope else self.parameters
        self.assets.add_or_replace_asset(Asset(filename=self.config_file_name, content=json.dumps(params)))

    def update_parameter(self, key: TJSONConfigKeyType, value: TJSONConfigValueType):
        """
        Update a parameter. The typehinting encourages JSON supported types

        Args:
            key: Config
            value:

        Returns:

        """
        self.parameters[key] = value

    def get_parameter(self, key: TJSONConfigKeyType) -> TJSONConfigValueType:
        """
        Returns a parameter value
        Args:
            key: Key of parameter

        Returns:
            Value of parameter
        Raises:
            KeyError
        """
        return self.parameters[key]

    def update_parameters(self, values: Dict[TJSONConfigKeyType, TJSONConfigValueType]):
        """
        Perform bulk update from another dictionary
        Args:
            values:

        Returns:

        """
        self.parameters.update(values)

    def reload_from_simulation(self, simulation: 'Simulation'):
        if simulation.platform:
            simulation.platform.get_files(simulation, self.config_file_name)


class JSONConfiguredTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredTask:
        return JSONConfiguredTask(**configuration)

    def get_description(self) -> str:
        return "Defines a general command that has a simple JSON based config"
