from logging import getLogger, DEBUG

from idmtools.entities.experiment import Experiment
from idmtools.registry import experiment_specification

logger = getLogger(__name__)


class ExperimentFactory:
    DEFAULT_KEY = 'idmtools.entities.experiment.Experiment'

    def __init__(self):
        from idmtools.registry.experiment_specification import ExperimentPlugins
        self._builders = ExperimentPlugins().get_plugin_map()
        aliases = dict()
        # register types as full paths as well
        for _model, spec in self._builders.items():
            aliases[f'{spec.get_type().__module__}.{spec.get_type().__name__}'] = spec
        self._builders.update(aliases)

    def create(self, key, fallback=None, **kwargs) -> Experiment:  # noqa: F821
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Attempting to create experiment of type {key}")
        if key is None:
            key = self.DEFAULT_KEY
            logger.warning(f'No experiment type tag found, assuming type: {key}')

        if key not in self._builders:
            if not fallback:
                raise ValueError(f"The ExperimentFactory could not create an experiment of type {key}")
            else:
                logger.warning(f'Could not find experiment type {key}. Using Fallback type of {fallback.__class__}')
                return fallback()

        model_spec: experiment_specification = self._builders.get(key)
        result = model_spec.get(kwargs)

        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Experiment created for type {key}")
        return result


experiment_factory = ExperimentFactory()
