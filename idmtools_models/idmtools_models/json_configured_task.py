"""idmtools json configured task.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import json
from dataclasses import dataclass, field, fields
from functools import partial
from logging import getLogger, DEBUG
from typing import Union, Dict, Any, List, Optional, Type, TYPE_CHECKING
from idmtools.assets import Asset, AssetCollection
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

TJSONConfigKeyType = Union[str, int, float]
TJSONConfigValueType = Union[str, int, float, Dict[TJSONConfigKeyType, Any]]

logger = getLogger(__name__)
user_logger = getLogger('user')


@dataclass
class JSONConfiguredTask(ITask):
    """
    Defines an extensible simple task that implements functionality through optional supplied use hooks.
    """

    # Note: large amounts of parameters will increase size of metadata
    parameters: dict = field(default_factory=lambda: {}, metadata={"md": True})
    envelope: str = field(default=None, metadata={"md": True})
    # If we don't define this we assume static name the script consuming file will know
    config_file_name: str = field(default="config.json", metadata={"md": True})
    # is the config file a common asset or a transient. We default ot transient
    is_config_common: bool = field(default=False)
    configfile_argument: str = field(default=None)
    # If command_line_argument is set, defines if we pass the filename after the argument
    # for example, if the argument is --config and the config file name is config.json we would run the command as
    # cmd --config config.json
    command_line_argument_no_filename: bool = field(default=False)

    def __post_init__(self):
        """Constructor."""
        super().__post_init__()
        if self.parameters is not None and self.envelope is not None and self.envelope in self.parameters:
            logger.debug(f'Loading parameters from envelope: {self.envelope}')
            self.parameters = self.parameters[self.envelope]

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather assets common across an Experiment(Set of Simulations).

        Returns:
            Common AssetCollection
        """
        if self.is_config_common:
            self.__dump_config(self.common_assets)
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather assets that are unique to this simulation/worktiem.

        Returns:
            Simulation/workitem level AssetCollection
        """
        self.__dump_config(self.transient_assets)
        return self.transient_assets

    def __dump_config(self, assets) -> None:
        """
        Writes the configuration out to asset.

        Args:
            assets: Asset to add configuration too

        Returns:
            None
        """
        if self.config_file_name is not None:
            params = {self.envelope: self.parameters} if self.envelope else self.parameters
            if logger.isEnabledFor(DEBUG):
                logger.debug('Adding JSON Configured File %s', self.config_file_name)
                logger.debug(f'Generating {self.config_file_name} as an asset from JSONConfiguredTask')
                logger.debug('Writing Config %s', json.dumps(params))
            assets.add_or_replace_asset(Asset(filename=self.config_file_name, content=json.dumps(params)))

    def set_parameter(self, key: TJSONConfigKeyType, value: TJSONConfigValueType):
        """
        Update a parameter. The type hinting encourages JSON supported types.

        Args:
            key: Config
            value:

        Returns:
            Tags to be defined on the simulation/workitem
        """
        if logger.isEnabledFor(DEBUG):
            logger.info('Setting parameter %s to %s', key, str(value))
        self.parameters[key] = value
        return {key: value}

    def get_parameter(self, key: TJSONConfigKeyType) -> TJSONConfigValueType:
        """
        Returns a parameter value.

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
        Perform bulk update from another dictionary.

        Args:
            values: Values to update as dictionaryy

        Returns:
            Values
        """
        if logger.isEnabledFor(DEBUG):
            for k, p in values.items():
                logger.debug('Setting parameter %s to %s', k, str(p))
        self.parameters.update(values)
        return values

    def reload_from_simulation(self, simulation: 'Simulation', config_file_name: Optional[str] = None,
                               envelope: Optional[str] = None, **kwargs):  # noqa: F821
        """
        Reload from Simulation.

        To do this, the process is

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
            self.parameters = self.__find_config(simulation)
            if envelope and envelope in self.parameters:
                self.parameters = self.parameters[envelope]
            elif 'task_envelope' in simulation.tags and simulation.tags['task_envelope'] in self.parameters:
                self.parameters = self.parameters[simulation.tags['task_envelope']]
            elif self.envelope and self.envelope in self.parameters:
                self.parameters = self.parameters[self.envelope]

    def __find_config(self, simulation: Simulation, config_file_name: str = None) -> Dict[str, Any]:
        """
        Used to rebuild configuration using simulation data that has been ran.

        Args:
            simulation: Simulation to load from
            config_file_name: Config file name

        Returns:
            Config reloaded
        """
        # find the ocnfig
        if config_file_name:
            cfn = config_file_name
        elif 'task_config_file_name' in simulation.tags:
            cfn = simulation.tags['task_config_file_name']
        else:
            cfn = self.config_file_name
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Loading Config from {simulation.id}:{cfn}')
        config = dict()
        if simulation.assets and isinstance(simulation.assets, (AssetCollection, list)):
            for file in simulation.assets:
                if file.filename == cfn:
                    config = file.content
                    if isinstance(config, bytes):
                        config = json.loads(config.decode('utf-8'))
            new_assets = []
            # filter our config from the simulation
            for _i, asset in enumerate(simulation.assets.assets):
                if asset.filename != cfn:
                    new_assets.append(asset)
            simulation.assets.assets = new_assets
        else:
            # try to load the config
            config = simulation.platform.get_files(simulation, [cfn])
            config = config[cfn]
            if isinstance(config, bytes):
                config = json.loads(config.decode('utf-8'))

        # filter config from transient assets
        if self.transient_assets:
            nw = AssetCollection()
            for asset in self.transient_assets:
                if isinstance(asset, dict) and asset['filename'] != cfn:
                    self.transient_assets.add_asset(Asset(**asset))
                elif isinstance(asset, Asset) and asset.filename != cfn:
                    self.transient_assets.add_asset(Asset(**asset))
            self.transient_assets = nw
        return config

    def pre_creation(self, parent: Union['Simulation', 'WorkflowItem'], platform: 'IPlatform'):  # noqa: F821
        """
        Pre-creation. For JSONConfiguredTask, we finalize our configuration file and command line here.

        Args:
            parent: Parent of task
            platform: Platform task is being created on

        Returns:
            None
        """
        defaults = [x for x in fields(JSONConfiguredTask) if x.name == "config_file_name"][0].default

        if self.config_file_name != defaults:
            logger.info('Found non-default name for config_file_name. Adding tag task_config_file_name')
            parent.tags['task_config_file_name'] = self.config_file_name

        if self.envelope:
            logger.info('Found envelope name. Adding tag envelope')
            parent.tags['task_envelope'] = self.envelope
        # Ensure our command line argument is added if configured
        if self.configfile_argument:
            logger.debug('Adding command_line_argument to command')
            if self.configfile_argument not in self.command.arguments:
                # check if we should add filename with arg?
                if self.command_line_argument_no_filename:
                    self.command.add_argument(self.configfile_argument)
                else:
                    self.command.add_argument(self.configfile_argument)
                    self.command.add_argument(self.config_file_name)

    def __repr__(self):
        """String version of task Prints config filename and parameters."""
        return f"<JSONConfiguredTask config:{self.config_file_name} parameters: {self.parameters}"

    @staticmethod
    def set_parameter_sweep_callback(simulation: Simulation, param: str, value: Any) -> Dict[str, Any]:
        """
        Performs a callback with a parameter and a value. Most likely users want to use set_parameter_partial instead of this method.

        Args:
            simulation: Simulation object
            param: Param name
            value: Value to set

        Returns:
            Tags to add to simulation
        """
        if not hasattr(simulation.task, 'set_parameter'):
            raise ValueError("update_task_with_set_parameter can only be used on tasks with a set_parameter")
        return simulation.task.set_parameter(param, value)

    @classmethod
    def set_parameter_partial(cls, parameter: str):
        """
        Callback to be used when sweeping with a json configured model.

        Args:
            parameter: Param name

        Returns:
            Partial setting a specific parameter

        Notes:
            - TODO Reference some examples code here
        """
        return partial(cls.set_parameter_sweep_callback, param=parameter)


class JSONConfiguredTaskSpecification(TaskSpecification):
    """
    JSONConfiguredTaskSpecification defines the plugin specs for JSONConfiguredTask.
    """

    def get(self, configuration: dict) -> JSONConfiguredTask:
        """
        Get instance of JSONConfiguredTask with configuration specified.

        Args:
            configuration: Configuration for configuration

        Returns:
            JSONConfiguredTask with configuration
        """
        return JSONConfiguredTask(**configuration)

    def get_description(self) -> str:
        """
        Get description for plugin.

        Returns:
            Description of plugin
        """
        return "Defines a general command that has a simple JSON based config"

    def get_example_urls(self) -> List[str]:
        """
        Get list of urls with examples for JSONConfiguredTask.

        Returns:
            List of urls that point to examples relating to JSONConfiguredTask
        """
        from idmtools_models import __version__
        examples = [f'examples/{example}' for example in ['python_model', 'load_lib']]
        return [self.get_version_url(f'v{__version__}', x) for x in examples]

    def get_type(self) -> Type[JSONConfiguredTask]:
        """
        Get task type provided by plugin.

        Returns:
            JSONConfiguredTask
        """
        return JSONConfiguredTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
