import json
from dataclasses import dataclass, field, fields
from functools import partial
from logging import getLogger, DEBUG
from typing import Union, Dict, Any, List, Optional, Type
from idmtools.assets import Asset, AssetCollection
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
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
        """
        Gather assets common across an Experiment(Set of Simulations)

        Returns:
            Common AssetCollection
        """
        if self.is_config_common:
            self.__dump_config(self.common_assets)
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather assets that are unique to this simulation/worktiem

        Returns:
            Simulation/workitem level AssetCollection
        """
        self.__dump_config(self.transient_assets)
        return self.transient_assets

    def __dump_config(self, assets) -> None:
        """
        Writes the configuration out to asset

        Args:
            assets: Asset to add configuration too

        Returns:
            None
        """
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

    def reload_from_simulation(self, simulation: 'Simulation', config_file_name: Optional[str] = None,
                               envelope: Optional[str] = None):  # noqa: F821
        """
        Reload from Simulation. To do this, the process is

         1. First check for a configfile name from arguments, then tags, or the default name
         2. Load the json config file
         3. Check if we got an envelope argument from parameters or the simulation tags, or on the task object

        Args:
            simulation: Simulation object with metadata to load info from
            config_file_name: Optional name of config file
            envelope: Optional name of envelope

        Returns:
            Populates the config with config from object
        """
        if simulation.platform:
            if config_file_name:
                cfn = config_file_name
            elif 'task_config_file_name' in simulation.tags:
                cfn = simulation.tags['task_config_file_name']
            else:
                cfn = self.config_file_name
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading Config from {simulation.id}:{cfn}')
            config = simulation.platform.get_files(simulation, cfn)

            self.parameters = config
            if envelope and envelope in self.parameters:
                self.parameters = self.parameters[envelope]
            elif 'task_envelope' in simulation.tags and simulation.tags['task_envelope'] in self.parameters:
                self.parameters = self.parameters[simulation.tags['task_envelope']]
            elif self.envelope and self.envelope in self.parameters:
                self.parameters = self.parameters[self.envelope]

    def pre_creation(self, parent: Union['Simulation', 'WorkflowItem']):  # noqa: F821
        defaults = [x for x in fields(JSONConfiguredTask) if x.name == "config_file_name"][0].default

        if self.config_file_name != defaults:
            logger.info('Found non-default name for config_file_name. Adding tag task_config_file_name')
            parent.tags['task_config_file_name'] = self.config_file_name

        if self.envelope:
            logger.info('Found envelope name. Adding tag envelope')
            parent.tags['task_envelope'] = self.envelope
        # Ensure our command line argument is added if configured
        if self.command_line_argument:
            logger.debug('Adding command_line_argument to command')
            if self.command_line_argument not in self.command.arguments:
                # check if we should add filename with arg?
                if self.command_line_argument_no_filename:
                    self.command.add_argument(self.command_line_argument)
                else:
                    self.command.add_option(self.command_line_argument, self.config_file_name)

    def __repr__(self):
        return f"<JSONConfiguredTask config:{self.config_file_name} parameters: {self.parameters}"

    @staticmethod
    def set_parameter_sweep_callback(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        if not hasattr(simulation.task, 'set_parameter'):
            raise ValueError("update_task_with_set_parameter can only be used on tasks with a set_parameter")
        return simulation.task.set_parameter(param, value)

    @classmethod
    def set_parameter_partial(cls, parameter: str):
        return partial(cls.set_parameter_sweep_callback, param=parameter)


class JSONConfiguredTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> JSONConfiguredTask:
        """
        Get instance of JSONConfiguredTask with configuration specified

        Args:
            configuration: Configuration for configuration

        Returns:
            JSONConfiguredTask with configuration
        """
        return JSONConfiguredTask(**configuration)

    def get_description(self) -> str:
        """
        Get description for plugin

        Returns:
            Description of plugin
        """
        return "Defines a general command that has a simple JSON based config"

    def get_example_urls(self) -> List[str]:
        """
        Get list of urls with examples for JSONConfiguredTask

        Returns:
            List of urls that point to examples relating to JSONConfiguredTask
        """
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['python_model', 'load_lib']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_type(self) -> Type[JSONConfiguredTask]:
        """
        Get task type provided by plugin

        Returns:
            JSONConfiguredTask
        """
        return JSONConfiguredTask
