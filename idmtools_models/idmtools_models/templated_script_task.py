import copy
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


@dataclass()
class TemplatedScriptTask(ITask):
    """
    Defines a task to run a script using a template. Best suited to shell scripts
    """
    # Name of script
    script_name: str = field(default=None)
    # a template string
    template: str = field(default=None)
    # a template file
    template_file: str = field(default=None)
    # Is the template a common asset or a transient asset
    template_is_common: bool = field(default=True)
    # template variables
    variables: Dict[str, Any] = field(default_factory=dict)
    path_sep: str = field(default='/')
    extra_command_arguments: str = field(default='')

    # Hooks to extend functionality
    gather_common_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)
    gather_transient_asset_hooks: List[Callable[[ITask], AssetCollection]] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if self.script_name is None and self.template_file is None:
            raise ValueError("Either script name or template file is required")
        elif self.script_name is None:  # Get name from the file
            self.script_name = os.path.basename(self.template_file)

        if self.template is None and self.template_file is None:
            raise ValueError("Either template or template_file is required")

        if self.template_file and not os.path.exists(self.template_file):
            raise FileNotFoundError(f"Could not find the file the template file {self.template_file}")

        if self.template_is_common:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Adding common asset hook")
            hook = partial(TemplatedScriptTask.__add_template_to_asset_collection, asset_collection=self.common_assets)
            self.gather_common_asset_hooks.append(hook)
        else:
            if logger.isEnabledFor(DEBUG):
                logger.debug("Adding transient asset hook")
            hook = partial(
                TemplatedScriptTask.__add_template_to_asset_collection,
                asset_collection=self.transient_assets
            )
            self.gather_transient_asset_hooks.append(hook)

    @staticmethod
    def __add_template_to_asset_collection(task: 'TemplatedScriptTask', asset_collection: AssetCollection) -> \
            AssetCollection:
        env = Environment()
        if task.template:
            template = env.from_string(task.template)
        else:
            template = env.get_template(task.template_file)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Rendering Script template: {template}")
        result = template.render(vars=task.variables, env=os.environ)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Rendered Template: {result}")

        asset = Asset(filename=task.script_name, content=result)
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
        if len(ac.assets) != 0:
            self.transient_assets = ac
        return ac

    def reload_from_simulation(self, simulation: 'Simulation'):  # noqa: F821
        pass

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        if self.template_is_common:
            sn = f'Assets{self.path_sep}{self.script_name}'
        else:
            sn = self.script_name
        self.command = CommandLine(sn)
        if self.extra_command_arguments:
            self.command.add_argument(self.extra_command_arguments)
        super().pre_creation(parent)


@dataclass()
class ScriptWrapperTask(ITask):
    template_script_task: TemplatedScriptTask = field(default=None)
    task: ITask = field(default=None)

    def __post_init__(self):
        if self.template_script_task is None:
            raise ValueError("Template Scrip Task is required")

        if self.task is None:
            raise ValueError("Task is required")

    def gather_common_assets(self):
        self.common_assets.add_assets(self.template_script_task.gather_common_assets())
        self.common_assets.add_assets(self.task.gather_common_assets())
        return self.common_assets

    def gather_transient_assets(self) -> AssetCollection:
        self.transient_assets.add_assets(self.template_script_task.gather_transient_assets())
        self.transient_assets.add_assets(self.task.gather_transient_assets())
        return self.transient_assets

    def reload_from_simulation(self, simulation: Simulation):
        # build simulations with fake objects
        sim = copy.deepcopy(simulation)
        sim.task = simulation.task.template_script_task
        simulation.task.reload_from_simulation(sim)
        simulation.task.template_script_task = sim.task.task

        sim = copy.deepcopy(simulation)
        sim.task = simulation.task.task
        simulation.task.reload_from_simulation(sim)
        simulation.task.task = sim.task.task

    def pre_creation(self, parent: Union[Simulation, IWorkflowItem]):
        self.task.pre_creation(parent)
        # get command from wrapper command and add to wrapper script as item we call as argument to script
        self.template_script_task.extra_command_arguments = str(self.task.command)
        self.template_script_task.pre_creation(parent)
        self.command = self.template_script_task.command

    def post_creation(self, parent: Union[Simulation, IWorkflowItem]):
        self.task.post_creation(parent)
        self.template_script_task.post_creation(parent)


def get_script_wrapper_task(task: ITask, wrapper_script_name: str, template_content: str = None,
                            template_file: str = None, template_is_common: bool = True,
                            variables: Dict[str, Any] = None, path_sep: str = '/') -> ScriptWrapperTask:
    if variables is None:
        variables = dict()
    template_task = TemplatedScriptTask(
        script_name=wrapper_script_name,
        template_file=template_file,
        template=template_content,
        template_is_common=template_is_common,
        variables=variables,
        path_sep=path_sep
    )
    return ScriptWrapperTask(template_script_task=template_task, task=task)


def get_script_wrapper_windows_task(task: ITask, wrapper_script_name: str = 'wrapper.bat', template_content: str = None,
                                    template_file: str = None, template_is_common: bool = True,
                                    variables: Dict[str, Any] = None) -> ScriptWrapperTask:
    """
    Get wrapper script task for windows platforms

    Args:
        task: Task to wrap
        wrapper_script_name: Wrapper script name(defaults to wrapper.bat)
        template_content:  Template Content
        template_file: Template File
        template_is_common: Is the template experiment level
        variables: Variables for template

    Returns:
        ScriptWrapperTask
    """
    return get_script_wrapper_task(task, wrapper_script_name, template_content, template_file, template_is_common,
                                   variables, "\\")


def get_script_wrapper_unix_task(task: ITask, wrapper_script_name: str = 'wrapper.sh', template_content: str = None,
                                 template_file: str = None, template_is_common: bool = True,
                                 variables: Dict[str, Any] = None):
    """
        Get wrapper script task for unix platforms

        Args:
            task: Task to wrap
            wrapper_script_name: Wrapper script name(defaults to wrapper.sh)
            template_content:  Template Content
            template_file: Template File
            template_is_common: Is the template experiment level
            variables: Variables for template

        Returns:
            ScriptWrapperTask
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
