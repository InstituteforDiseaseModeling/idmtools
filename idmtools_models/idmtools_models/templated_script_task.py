import shlex
import os
from dataclasses import dataclass, field
from functools import partial
from logging import getLogger, DEBUG
from typing import List, Callable, Type, Dict, Any, Union
from jinja2 import Environment
from idmtools.assets import AssetCollection, Asset
from idmtools.entities import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)

DICT_TO_ENVIRONMENT = """{% for key, value in vars.items() %}
export {{key}}="{{value}}"
{% endfor %}
"""

# Define our common windows templates
WINDOWS_BASE_WRAPPER = """echo Running %*
\"%*\""""
WINDOWS_PYTHON_PATH_WRAPPER = """set PYTHONPATH=%cd%\\Assets\\site-packages\\;%cd%\\Assets\\;%PYTHONPATH%
{}""".format(WINDOWS_BASE_WRAPPER)
WINDOWS_DICT_TO_ENVIRONMENT = DICT_TO_ENVIRONMENT + WINDOWS_BASE_WRAPPER

# Define our linux common scripts
LINUX_BASE_WRAPPER = """echo Running $@
\"$@\"
"""
LINUX_PYTHON_PATH_WRAPPER = """export PYTHONPATH=$(pwd)/Assets/site-packages:$(pwd)/Assets/:$PYTHONPATH
{}""".format(LINUX_BASE_WRAPPER)
LINUX_DICT_TO_ENVIRONMENT = DICT_TO_ENVIRONMENT + LINUX_BASE_WRAPPER


@dataclass()
class TemplatedScriptTask(ITask):
    """
    Defines a task to run a script using a template. Best suited to shell scripts

    Examples:
        .. literalinclude:: ../examples/cookbook/python/python-path/python-path.py

        .. literalinclude:: ../examples/cookbook/environment/variables/environment-vars.py
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
        Add our rendered template to the asset collection
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
        Gather common(experiment-level) assets for task

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
        Gather transient(experiment-level) assets for task

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
        Reload a templated script task. When reloading, you will only have the rendered template available

        Args:
            simulation:

        Returns:

        """
        # check experiment level assets for our script
        if simulation.parent.assets:
            # prep new asset collection in case we have to remove our asset from the experiment level
            new_assets = AssetCollection()
            for i, asset in enumerate(simulation.parent.assets.assets):
                # is it our script?
                if asset.filename != self.script_path and asset.absolute_path != self.script_path:
                    # nope keep it
                    new_assets.add_asset(asset)
            # set filtered assets back to parent
            simulation.parent.assets = new_assets

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        """
        Before creating simulation, we need to set our command line

        Args:
            parent: Parent object

        Returns:

        """
        # are we experiment or simulation level asset?
        if self.script_binary:
            sn = self.script_binary + ' '
        else:
            sn = ''
        if self.template_is_common:
            sn += f'Assets{self.path_sep}{self.script_path}'
        else:
            sn += self.script_path
        # set the command line to the rendered script
        self.command = CommandLine(sn)
        # set any extra arguments
        if self.extra_command_arguments:
            self.command.add_argument(self.extra_command_arguments)
        # run base precreation
        super().pre_creation(parent)


@dataclass()
class ScriptWrapperTask(ITask):
    """
    Allows you to wrap a script with another script


    See Also:
        :py:class:`idmtools_models.templated_script_task.TemplatedScriptTask`

    Raises:
        ValueError if the template Script Task is not defined
    """
    template_script_task: TemplatedScriptTask = field(default=None)
    task: ITask = field(default=None)

    def __post_init__(self):
        if self.template_script_task is None:
            raise ValueError("Template Script Task is required")

        if self.task is None:
            raise ValueError("Task is required")

    def gather_common_assets(self):
        """
        Gather all the common assets
        Returns:

        """
        self.common_assets.add_assets(self.template_script_task.gather_common_assets())
        self.common_assets.add_assets(self.task.gather_common_assets())
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        """
        Gather all the transient assets
        Returns:

        """
        self.transient_assets.add_assets(self.template_script_task.gather_transient_assets())
        self.transient_assets.add_assets(self.task.gather_transient_assets())
        return self.transient_assets

    def reload_from_simulation(self, simulation: Simulation):
        """
        Reload from simulation

        Args:
            simulation: simulation

        Returns:

        """
        from idmtools.core.task_factory import TaskFactory
        # check if the task is a dict
        if isinstance(simulation.task.task, dict):
            # process sub task first
            task_args = {k: v for k, v in simulation.task.task.items() if k not in ['task_type']}
            simulation.task.task = TaskFactory().create(simulation.task.task['task_type'], **task_args)
            simulation.task.task.reload_from_simulation(simulation)

            simulation.task.template_script_task = simulation.task.task
        else:
            logger.warning("Unable to load subtask")

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        """
        Before creation, create the true command by adding the wrapper name

        Args:
            parent:

        Returns:

        """
        self.task.pre_creation(parent)
        # get command from wrapper command and add to wrapper script as item we call as argument to script
        self.template_script_task.extra_command_arguments = str(self.task.command)
        self.template_script_task.pre_creation(parent)
        self.command = self.template_script_task.command

    def post_creation(self, parent: Union[Simulation, IWorkflowItem]):
        self.task.post_creation(parent)
        self.template_script_task.post_creation(parent)

    def __getattr__(self, item):
        if item not in self.__dict__:
            return getattr(self.task, item)
        else:
            return super(ScriptWrapperTask, self).__getattr__(item)


def get_script_wrapper_task(task: ITask, wrapper_script_name: str, template_content: str = None,
                            template_file: str = None, template_is_common: bool = True,
                            variables: Dict[str, Any] = None, path_sep: str = '/') -> ScriptWrapperTask:
    """
    Convenience function that will wrap a task for you with some defaults

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
                                    template_content: str = WINDOWS_BASE_WRAPPER,
                                    template_file: str = None, template_is_common: bool = True,
                                    variables: Dict[str, Any] = None) -> ScriptWrapperTask:
    """
    Get wrapper script task for windows platforms

    The default content wraps a batch script that just passes on to actual task. To modify python path, use WINDOWS_PYTHON_PATH_WRAPPER

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


def get_script_wrapper_unix_task(task: ITask, wrapper_script_name: str = 'wrapper.sh', template_content: str = LINUX_BASE_WRAPPER,
                                 template_file: str = None, template_is_common: bool = True,
                                 variables: Dict[str, Any] = None):
    """
        Get wrapper script task for unix platforms

        The default content wraps a bash script just passes options to a script. To modify python path, you can use LINUX_PYTHON_PATH_WRAPPER

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
        :func:`idmtools_models.templated_script_task.get_script_wrapper_task`
        :func:`idmtools_models.templated_script_task.get_script_wrapper_windows_task`
        """
    return get_script_wrapper_task(task, wrapper_script_name, template_content, template_file, template_is_common,
                                   variables, "/")


class TemplatedScriptTaskSpecification(TaskSpecification):
    def get(self, configuration: dict) -> TemplatedScriptTask:
        """
        Get instance of TemplatedScriptTask with configuration

        Args:
            configuration: configuration for TemplatedScriptTask

        Returns:
            TemplatedScriptTask with configuration
        """
        return TemplatedScriptTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin

        Returns:
            Plugin description
        """
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"

    def get_example_urls(self) -> List[str]:
        """
        Get example urls related to TemplatedScriptTask

        Returns:
            List of urls that have examples related to CommandTask
        """
        return []

    def get_type(self) -> Type[TemplatedScriptTask]:
        """
        Get task type provided by plugin

        Returns:
            TemplatedScriptTask
        """
        return TemplatedScriptTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__


class ScriptWrapperTaskSpecification(TaskSpecification):
    def get(self, configuration: dict) -> ScriptWrapperTask:
        """
        Get instance of ScriptWrapperTask with configuration

        Args:
            configuration: configuration for ScriptWrapperTask

        Returns:
            TemplatedScriptTask with configuration
        """
        return ScriptWrapperTask(**configuration)

    def get_description(self) -> str:
        """
        Get description of plugin

        Returns:
            Plugin description
        """
        return "Defines a general command that provides user hooks. Intended for use in advanced scenarios"

    def get_example_urls(self) -> List[str]:
        """
        Get example urls related to ScriptWrapperTask

        Returns:
            List of urls that have examples related to CommandTask
        """
        return []

    def get_type(self) -> Type[ScriptWrapperTask]:
        """
        Get task type provided by plugin

        Returns:
            TemplatedScriptTask
        """
        return ScriptWrapperTask

    def get_version(self) -> str:
        """
        Returns the version of the plugin

        Returns:
            Plugin Version
        """
        from idmtools_models import __version__
        return __version__
