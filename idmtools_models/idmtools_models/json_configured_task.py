import json
from dataclasses import dataclass, field
from logging import getLogger, DEBUG
from typing import Union, Dict, Any

from idmtools.assets import Asset, AssetCollection
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
    # If we don't define this we assume static name the script consuming file will know
    config_file_name: str = field(default="config.json")
    # is the config file a common asset or a transient. We default ot transient
    is_config_common: bool = field(default=False)
    command_line_argument: str = field(default=None)
    # If command_line_argument is set, defines if we pass the filename after the argument
    # for example, if the argument is --config and the config file name is config.json we would run the command as
    # cmd --config config.json
    command_line_argument_no_filename: bool = field(default=True)

    def __post_init__(self):
        super().__post_init__()
        if self.parameters is not None and self.envelope is not None and self.envelope in self.parameters:
            logger.debug(f'Loading parameters from envelope: {self.envelope}')
            self.parameters = self.parameters[self.envelope]

    def gather_common_assets(self) -> AssetCollection:
        if self.is_config_common:
            self.__dump_config(self.common_assets)
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Here we dump our config
        """
        self.__dump_config(self.transient_assets)
        return self.transient_assets

    def __dump_config(self, assets):
        if self.config_file_name is not None:
            params = {self.envelope: self.parameters} if self.envelope else self.parameters
            self._task_log.info('Adding JSON Configured File %s', self.config_file_name)
            if logger.isEnabledFor(DEBUG):
                logger.info(f'Generating {self.config_file_name} as an asset from JSONConfiguredTask')
                self._task_log.debug('Writing Config %s', json.dumps(params))
            assets.add_or_replace_asset(Asset(filename=self.config_file_name, content=json.dumps(params)))

    def set_parameter(self, key: TJSONConfigKeyType, value: TJSONConfigValueType):
        """
        Update a parameter. The type hinting encourages JSON supported types

        Args:
            key: Config
            value:

        Returns:

        """
        self._task_log.info('Setting parameter %s to %s', key, str(value))
        self.parameters[key] = value
        return {key: value}

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
        for k, p in values.items():
            self._task_log.info('Setting parameter %s to %s', k, str(p))
        self.parameters.update(values)
        return values

    def reload_from_simulation(self, simulation: 'Simulation'):  # noqa: F821
        if simulation.platform:
            simulation.platform.get_files(simulation, self.config_file_name)

    def pre_creation(self, parent: Union['Simulation', 'WorkflowItem']):
        # Ensure our command line argument is added if configured
        if self.command_line_argument:
            if self.command_line_argument not in self.command.arguments:
                # check if we should add filename with arg?
                if self.command_line_argument_no_filename:
                    self.command.add_argument(self.command_line_argument)
                else:
                    self.command.add_option(self.command_line_argument, self.config_file_name)

    def __repr__(self):
        return f"<JSONConfiguredTask config:{self.config_file_name} parameters: {self.parameters}"


class JSONConfiguredTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredTask:
        return JSONConfiguredTask(**configuration)

    def get_description(self) -> str:
        return "Defines a general command that has a simple JSON based config"
