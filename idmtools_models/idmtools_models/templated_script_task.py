"""Provides the TemplatedScriptTask.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
import inspect
import os
from contextlib import suppress
from dataclasses import dataclass, field
from functools import partial
from logging import getLogger, DEBUG
from typing import List, Callable, Type, Dict, Any, Union, TYPE_CHECKING
from jinja2 import Environment
from idmtools.assets import AssetCollection, Asset
from idmtools.entities import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification
if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)

LINUX_DICT_TO_ENVIRONMENT = """{% for key, value in vars.items() %}
export {{key}}="{{value}}"
{% endfor %}
"""

WINDOWS_DICT_TO_ENVIRONMENT = """{% for key, value in vars.items() %}
set {{key}}="{{value}}"
{% endfor %}
"""

# Define our common windows templates
WINDOWS_BASE_WRAPPER = """echo Running %*
%*"""
WINDOWS_PYTHON_PATH_WRAPPER = """set PYTHONPATH=%cd%\\Assets\\site-packages\\;%cd%\\Assets\\;%PYTHONPATH%
{}""".format(WINDOWS_BASE_WRAPPER)
WINDOWS_DICT_TO_ENVIRONMENT = WINDOWS_DICT_TO_ENVIRONMENT + WINDOWS_BASE_WRAPPER

# Define our linux common scripts
LINUX_BASE_WRAPPER = """echo Running args $@
\"$@\"
"""
LINUX_PYTHON_PATH_WRAPPER = """export PYTHONPATH=$(pwd)/Assets/site-packages:$(pwd)/Assets/:$PYTHONPATH
{}""".format(LINUX_BASE_WRAPPER)
LINUX_DICT_TO_ENVIRONMENT = LINUX_DICT_TO_ENVIRONMENT + LINUX_BASE_WRAPPER


@dataclass()
class TemplatedScriptTask(ITask):
    """
    Defines a task to run a script using a template. Best suited to shell scripts.

    Examples:
        In this example, we add modify the Python Path using TemplatedScriptTask and LINUX_PYTHON_PATH_WRAPPER

        .. literalinclude:: ../../examples/cookbook/python/python-path/python-path.py

        In this example, we modify environment variable using TemplatedScriptTask and LINUX_DICT_TO_ENVIRONMENT

        .. literalinclude:: ../../examples/cookbook/environment/variables/environment-vars.py
    """
    #: Name of script
    script_path: str = field(default=None, metadata={"md": True})
    #: If platform requires path to script executing binary(ie /bin/bash)
    script_binary: str = field(default=None, metadata={"md": True})
    #: The template contents
    template: str = field(default=None, metadata={"md": True})
    #: The template file. You can only use either template or template_file at once
    template_file: str = field(default=None, metadata={"md": True})
    #: Controls whether a template should be an experiment or a simulation level asset
    template_is_common: bool = field(default=True, metadata={"md": True})
    #: Template variables used for rendering the template
    # Note: large amounts of variables will increase metadata size
    variables: Dict[str, Any] = field(default_factory=dict, metadata={"md": True})
    #: Platform Path Separator. For Windows execution platforms, use \, otherwise use the default of /
    path_sep: str = field(default='/', metadata={"md": True})
    #: Extra arguments to add to the command line
    extra_command_arguments: str = field(default='', metadata={"md": True})

    #: Hooks to gather common assets
    gather_common_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)
    #: Hooks to gather transient assets
    gather_transient_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)

    def __post_init__(self):
        """Constructor."""
        super().__post_init__()
        if self.script_path is None and self.template_file is None:
            raise ValueError("Either script name or template file is required")
        elif self.script_path is None:  # Get name from the file
            self.script_path = os.path.basename(self.template_file)

        if self.template is None and self.template_file is None:
            raise ValueError("Either template or template_file is required")

        if self.template_file and not os.path.exists(self.template_file):
            raise FileNotFoundError(f"Could not find the file the template file {self.template_file}")

        # is the template a common(experiment) asset?
        if self.template_is_common:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Adding common asset hook")
            # add hook to render it to common asset hooks
            hook = partial(TemplatedScriptTask._add_template_to_asset_collection, asset_collection=self.common_assets)
            self.gather_common_asset_hooks.append(hook)
        else:
            # it must be a simulation level asset
            if logger.isEnabledFor(DEBUG):
                logger.debug("Adding transient asset hook")
            # create hook to render it to our transient assets
            hook = partial(
                TemplatedScriptTask._add_template_to_asset_collection,
                asset_collection=self.transient_assets
            )
            # add the hook
            self.gather_transient_asset_hooks.append(hook)

    @staticmethod
    def _add_template_to_asset_collection(task: 'TemplatedScriptTask', asset_collection: AssetCollection) -> \
            AssetCollection:
        """
        Add our rendered template to the asset collection.

        Args:
            task: Task to add
            asset_collection:Asset collection

        Returns:
            Asset Collection with template added
        """
        # setup our jinja environment
        env = Environment()
        # try to load template from string or file
        if task.template:
            template = env.from_string(task.template)
        else:
            template = env.get_template(task.template_file)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Rendering Script template: {template}")
        # render the template
        result = template.render(vars=task.variables, env=os.environ)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Rendered Template: {result}")

        # create an asset
        asset = Asset(filename=task.script_path, content=result)
        asset_collection.add_asset(asset)
        return asset_collection

    def gather_common_assets(self) -> AssetCollection:
        """
        Gather common(experiment-level) assets for task.

        Returns:
            AssetCollection containing common assets
        """
        # TODO validate hooks have expected return type
        ac = AssetCollection()
        for x in self.gather_common_asset_hooks:
            ac += x(self)
        return ac

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather transient(experiment-level) assets for task.

        Returns:
            AssetCollection containing transient assets
        """
        ac = AssetCollection()
        for x in self.gather_transient_asset_hooks:
            ac += x(self)
        ac += self.transient_assets
        if len(ac.assets) != 0:
            self.transient_assets = ac
        return ac

    def reload_from_simulation(self, simulation: Simulation):
        """
        Reload a templated script task. When reloading, you will only have the rendered template available.

        Args:
            simulation:

        Returns:
            None
        """
        # check experiment level assets for our script
        if simulation.parent.assets:
            # prep new asset collection in case we have to remove our asset from the experiment level
            new_assets = AssetCollection()
            for _i, asset in enumerate(simulation.parent.assets.assets):
                # is it our script?
                if asset.filename != self.script_path and asset.absolute_path != self.script_path:
                    # nope keep it
                    new_assets.add_asset(asset)
            # set filtered assets back to parent
            simulation.parent.assets = new_assets

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Before creating simulation, we need to set our command line.

        Args:
            parent: Parent object
            platform: Platform item is being ran on
        Returns:

        """
        # are we experiment or simulation level asset?
        if self.script_binary:
            sn = self.script_binary + ' '
        else:
            sn = ''
        if self.template_is_common:
            sn += platform.join_path(platform.common_asset_path, self.script_path)
        else:
            sn += self.script_path
        # set the command line to the rendered script
        self.command = CommandLine.from_string(sn)
        if self.path_sep != "/":
            self.command.executable = self.command.executable.replace("/", self.path_sep)
            self.command.is_windows = True
        # set any extra arguments
        if self.extra_command_arguments:
            other_command = CommandLine.from_string(self.extra_command_arguments)
            self.command._args.append(other_command.executable)
            if other_command._options:
                self.command._args += other_command._options
            if other_command._args:
                self.command._args += other_command._args
        super().pre_creation(parent, platform)


@dataclass()
class ScriptWrapperTask(ITask):
    """
    Allows you to wrap a script with another script.

    See Also:
        :py:class:`idmtools_models.templated_script_task.TemplatedScriptTask`

    Raises:
        ValueError if the template Script Task is not defined
    """
    template_script_task: TemplatedScriptTask = field(default=None)
    task: ITask = field(default=None)

    def __post_init__(self):
        """Constructor."""
        if self.template_script_task is None:
            raise ValueError("Template Script Task is required")

        if self.task is None:
            raise ValueError("Task is required")

        if isinstance(self.task, dict):
            self.task = self.from_dict(self.task)
        if isinstance(self.template_script_task, dict):
            self.template_script_task = self.from_dict(self.template_script_task)

    @staticmethod
    def from_dict(task_dictionary: Dict[str, Any]):
        """Load the task from a dictionary."""
        from idmtools.core.task_factory import TaskFactory
        task_args = {k: v for k, v in task_dictionary.items() if k not in ['task_type']}
        return TaskFactory().create(task_dictionary['task_type'], **task_args)

    @property
    def command(self):
        """Our task property. Again, we have to overload this because of wrapping a task."""
        cmd = copy.deepcopy(self.template_script_task.command)
        cmd.add_raw_argument(str(self.task.command))
        return cmd

    @command.setter
    def command(self, value: Union[str, CommandLine]):
        """Set our command. because we are wrapping a task, we have to overload this."""
        callers = []
        with suppress(KeyError, IndexError):
            callers = inspect.stack()[1:3]
        if not callers or callers[0].filename == __file__ or callers[1].filename == __file__:
            if isinstance(value, property):
                self._command = None
            elif isinstance(value, str):
                self._command = CommandLine.from_string(value)
            else:
                self._command = value
        else:
            self.task.command = value

    @property
    def wrapped_task(self):
        """
        Our task we are wrapping with a shell script.

        Returns:
            Our wrapped task
        """
        return self.task

    @wrapped_task.setter
    def wrapped_task(self, value: ITask):
        """Set our wrapped task."""
        return None if isinstance(value, property) else value

    def gather_common_assets(self):
        """
        Gather all the common assets.

        Returns:
            Common assets(Experiment Assets)
        """
        self.common_assets.add_assets(self.template_script_task.gather_common_assets())
        self.common_assets.add_assets(self.task.gather_common_assets())
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather all the transient assets.

        Returns:
            Transient Assets(Simulation level assets)
        """
        self.transient_assets.add_assets(self.template_script_task.gather_transient_assets())
        self.transient_assets.add_assets(self.task.gather_transient_assets())
        return self.transient_assets

    def reload_from_simulation(self, simulation: Simulation):
        """
        Reload from simulation.

        Args:
            simulation: simulation

        Returns:
            None
        """
        pass

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Before creation, create the true command by adding the wrapper name.

        Here we call both our wrapped task and our template_script_task pre_creation
        Args:
            parent: Parent Task
            platform: Platform Templated Task is executing on

        Returns:
            None
        """
        self.task.pre_creation(parent, platform)
        self.template_script_task.pre_creation(parent, platform)

    def post_creation(self, parent: Union[Simulation, IWorkflowItem], platform: 'IPlatform'):
        """
        Post creation of task.

        Here we call both our wrapped task and our template_script_task post_creation

        Args:
            parent: Parent of task
            platform: Platform we are running on

        Returns:
            None
        """
        self.task.post_creation(parent, platform)
        self.template_script_task.post_creation(parent, platform)

    def __getattr__(self, item):
        """Proxy get attr to child except for task item and items not in our object."""
        if item not in self.__dict__:
            return getattr(self.task, item)
        else:
            return super(ScriptWrapperTask, self).__getattr__(item)


def get_script_wrapper_task(task: ITask, wrapper_script_name: str, template_content: str = None,
                            template_file: str = None, template_is_common: bool = True,
                            variables: Dict[str, Any] = None, path_sep: str = '/') -> ScriptWrapperTask:
    """
    Convenience function that will wrap a task for you with some defaults.

    Args:
        task: Task to wrap
        wrapper_script_name: Wrapper script name
        template_content:  Template Content
        template_file: Template File
        template_is_common: Is the template experiment level
        variables: Variables
        path_sep: Path sep(Window or Linux)

    Returns:
        ScriptWrapperTask wrapping the task

    See Also:
        :class:`idmtools_models.templated_script_task.TemplatedScriptTask`
        :func:`idmtools_models.templated_script_task.get_script_wrapper_windows_task`
        :func:`idmtools_models.templated_script_task.get_script_wrapper_unix_task`
    """
    if variables is None:
        variables = dict()
    template_task = TemplatedScriptTask(
        script_path=wrapper_script_name,
        template_file=template_file,
        template=template_content,
        template_is_common=template_is_common,
        variables=variables,
        path_sep=path_sep
    )
    return ScriptWrapperTask(template_script_task=template_task, task=task)


def get_script_wrapper_windows_task(task: ITask, wrapper_script_name: str = 'wrapper.bat',
                                    template_content: str = WINDOWS_DICT_TO_ENVIRONMENT,
                                    template_file: str = None, template_is_common: bool = True,
                                    variables: Dict[str, Any] = None) -> ScriptWrapperTask:
    """
    Get wrapper script task for windows platforms.

    The default content wraps a another task with a batch script that exports the variables to the run environment defined in variables. To modify python path, use WINDOWS_PYTHON_PATH_WRAPPER

    You can adapt this script to modify any pre-scripts you need or call others scripts in succession

    Args:
        task: Task to wrap
        wrapper_script_name: Wrapper script name(defaults to wrapper.bat)
        template_content:  Template Content.
        template_file: Template File
        template_is_common: Is the template experiment level
        variables: Variables for template

    Returns:
        ScriptWrapperTask

    See Also::
        :class:`idmtools_models.templated_script_task.TemplatedScriptTask`
        :func:`idmtools_models.templated_script_task.get_script_wrapper_task`
        :func:`idmtools_models.templated_script_task.get_script_wrapper_unix_task`
    """
    return get_script_wrapper_task(task, wrapper_script_name, template_content, template_file, template_is_common,
                                   variables, "\\")


def get_script_wrapper_unix_task(task: ITask, wrapper_script_name: str = 'wrapper.sh', template_content: str = LINUX_DICT_TO_ENVIRONMENT,
                                 template_file: str = None, template_is_common: bool = True,
                                 variables: Dict[str, Any] = None):
    """
    Get wrapper script task for unix platforms.

    The default content wraps a another task with a bash script that exports the variables to the run environment defined in variables. To modify python path, you can use LINUX_PYTHON_PATH_WRAPPER

    You can adapt this script to modify any pre-scripts you need or call others scripts in succession

    Args:
        task: Task to wrap
        wrapper_script_name: Wrapper script name(defaults to wrapper.sh)
        template_content:  Template Content
        template_file: Template File
        template_is_common: Is the template experiment level
        variables: Variables for template

    Returns:
        ScriptWrapperTask

    See Also:
    :class:`idmtools_models.templated_script_task.TemplatedScriptTask`
    :func:`idmtools_models.templated_script_task.get_script_wrapper_task`
    :func:`idmtools_models.templated_script_task.get_script_wrapper_windows_task`
    """
    return get_script_wrapper_task(task, wrapper_script_name, template_content, template_file, template_is_common,
                                   variables, "/")


class TemplatedScriptTaskSpecification(TaskSpecification):
    """
    TemplatedScriptTaskSpecification provides the plugin specs for TemplatedScriptTask.
    """

    def get(self, configuration: dict) -> TemplatedScriptTask:
        """
        Get instance of TemplatedScriptTask with configuration.

        Args:
            configuration: configuration for TemplatedScriptTask

        Returns:
            TemplatedScriptTask with configuration
        """
        return TemplatedScriptTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin.

        Returns:
            Plugin description
        """
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"

    def get_example_urls(self) -> List[str]:
        """
        Get example urls related to TemplatedScriptTask.

        Returns:
            List of urls that have examples related to CommandTask
        """
        return []

    def get_type(self) -> Type[TemplatedScriptTask]:
        """
        Get task type provided by plugin.

        Returns:
            TemplatedScriptTask
        """
        return TemplatedScriptTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__


class ScriptWrapperTaskSpecification(TaskSpecification):
    """
    ScriptWrapperTaskSpecification defines the plugin specs for ScriptWrapperTask.
    """

    def get(self, configuration: dict) -> ScriptWrapperTask:
        """
        Get instance of ScriptWrapperTask with configuration.

        Args:
            configuration: configuration for ScriptWrapperTask

        Returns:
            TemplatedScriptTask with configuration
        """
        return ScriptWrapperTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin.

        Returns:
            Plugin description
        """
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"

    def get_example_urls(self) -> List[str]:
        """
        Get example urls related to ScriptWrapperTask.

        Returns:
            List of urls that have examples related to CommandTask
        """
        return []

    def get_type(self) -> Type[ScriptWrapperTask]:
        """
        Get task type provided by plugin.

        Returns:
            TemplatedScriptTask
        """
        return ScriptWrapperTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin.

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
