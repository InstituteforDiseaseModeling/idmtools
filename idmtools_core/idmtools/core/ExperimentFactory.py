import typing
from logging import getLogger

from idmtools.registry import ModelSpecification

if typing.TYPE_CHECKING:
    from idmtools.core import TExperimentClass, TExperiment


logger = getLogger(__name__)


class ExperimentFactory:
    def __init__(self):
        from idmtools.registry.ModelSpecification import ModelPlugins
        self._builders = ModelPlugins().get_plugin_map()

    def create(self, key, **kwargs) -> 'TExperiment':
        if key not in self._builders:
            raise ValueError(f"The ExperimentFactory could not create an experiment of type {key}")

        model_spec:ModelSpecification = self._builders.get(key)
        return model_spec.get(kwargs)


experiment_factory = ExperimentFactory()
