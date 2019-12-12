from logging import getLogger
from idmtools.entities import IExperiment
from idmtools.registry import model_specification

logger = getLogger(__name__)


class ExperimentFactory:

    DEFAULT_KEY = 'idmtools_model_emod.emod_experiment.EMODExperiment'

    def __init__(self):
        from idmtools.registry.model_specification import ModelPlugins
        self._builders = ModelPlugins().get_plugin_map()
        aliases = dict()
        # register types as full paths as well
        for model, spec in self._builders.items():
            aliases[f'{spec.get_type().__module__}.{spec.get_type().__name__}'] = spec
        self._builders.update(aliases)

    def create(self, key, fallback=None, **kwargs) -> IExperiment:  # noqa: F821
        if key is None:
            key = self.DEFAULT_KEY
            logger.warning(f'No experiment type tag found, assuming type: {key}')

        if key not in self._builders:
            if not fallback:
                raise ValueError(f"The ExperimentFactory could not create an experiment of type {key}")
            else:
                return fallback()

        model_spec: model_specification = self._builders.get(key)
        return model_spec.get(kwargs)


experiment_factory = ExperimentFactory()
