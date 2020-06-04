from logging import getLogger
from typing import NoReturn, Type

from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)
TASK_BUILDERS = None


class DynamicTaskSpecification(TaskSpecification):
    """
    This class allows users to quickly define a spec for special tasks
    """

    def __init__(self, task_type: Type[ITask], description: str = ''):
        self.task_type = task_type
        self.description = description

    def get(self, configuration: dict) -> ITask:
        return self.task_type(**configuration)

    def get_description(self) -> str:
        return self.description

    def get_type(self) -> Type[ITask]:
        return self.task_type


class TaskFactory:

    DEFAULT_KEY = 'idmtools.entities.command_task.CommandTask'

    def __init__(self):
        global TASK_BUILDERS
        if TASK_BUILDERS is None:
            from idmtools.registry.task_specification import TaskPlugins
            TASK_BUILDERS = TaskPlugins().get_plugin_map()
        self._builders = TASK_BUILDERS
        aliases = dict()
        # register types as full paths as well
        for model, spec in self._builders.items():
            try:
                aliases[f'{spec.get_type().__module__}.{spec.get_type().__name__}'] = spec
            except Exception as e:
                logger.warning(f"Could not load alias for {spec}")
                logger.exception(e)
        self._builders.update(aliases)

    def register(self, spec: TaskSpecification) -> NoReturn:
        """
        Register a TaskSpecification dynamically

        Args:
            spec: Specification to register

        Returns:

        """
        type_name = spec.get_type().__name__
        module_name = {spec.get_type().__module__}
        logger.debug(f'Registering task: {type_name} as both {type_name} and as {module_name}.{type_name}')
        self._builders[type_name] = spec
        self._builders[f'{module_name}.{type_name}'] = spec

    def register_task(self, task: Type[ITask]) -> NoReturn:
        """
        Dynamically register a class using the DynamicTaskSpecification

        Args:
            task: Task to register

        Returns:

        """
        spec = DynamicTaskSpecification(task)
        self.register(spec)

    def create(self, key, fallback=None, **kwargs) -> ITask:  # noqa: F821
        if key is None:
            key = self.DEFAULT_KEY
            logger.warning(f'No task type tag found, assuming type: {key}')

        if key not in self._builders:
            if not fallback:
                raise ValueError(f"The TaskFactory could not create an task of type {key}")
            else:
                return fallback()

        task_spec: TaskSpecification = self._builders.get(key)
        return task_spec.get(kwargs)


task_factory = TaskFactory()
