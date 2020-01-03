from logging import getLogger
from idmtools.entities.itask import ITask
from idmtools.registry.task_specification import TaskSpecification

logger = getLogger(__name__)


class TaskFactory:

    DEFAULT_KEY = 'idmtools.entities.command_task.CommandTask'

    def __init__(self):
        from idmtools.registry.task_specification import TaskPlugins
        self._builders = TaskPlugins().get_plugin_map()
        aliases = dict()
        # register types as full paths as well
        for model, spec in self._builders.items():
            aliases[f'{spec.get_type().__module__}.{spec.get_type().__name__}'] = spec
        self._builders.update(aliases)

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
