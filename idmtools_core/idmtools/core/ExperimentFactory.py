from logging import getLogger

from idmtools.registry import ModelSpecification

logger = getLogger(__name__)


class ExperimentFactory:
    def __init__(self):
        from idmtools.registry.ModelSpecification import ModelPlugins
        self._builders = ModelPlugins().get_plugin_map()
        aliases = dict()
        # register types as full paths as well
        for model, spec in self._builders.items():
            aliases[spec.get_type().__module__] = spec
        self._builders.update(aliases)

    def create(self, key, **kwargs) -> 'TExperiment':  # noqa: F821
        if key not in self._builders:
            raise ValueError(f"The ExperimentFactory could not create an experiment of type {key}")

        model_spec: ModelSpecification = self._builders.get(key)
        return model_spec.get(kwargs)


experiment_factory = ExperimentFactory()
