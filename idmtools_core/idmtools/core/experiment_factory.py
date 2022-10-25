"""
Define ExperimentFactory.

This is used mostly internally. It does allow us to support specialized experiment types when needed.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from logging import getLogger, DEBUG
from idmtools.entities.experiment import Experiment
from idmtools.registry import experiment_specification

logger = getLogger(__name__)


class ExperimentFactory:
    """
    ExperimentFactory allows creating experiments that could be derived through plugins.

    """
    DEFAULT_KEY = 'idmtools.entities.experiment.Experiment'

    def __init__(self):
        """
        Initialize our factory.

        On initialize, we load our plugin and build a map of ids for experiments.
        """
        from idmtools.registry.experiment_specification import ExperimentPlugins
        self._builders = ExperimentPlugins().get_plugin_map()
        aliases = dict()
        # register types as full paths as well
        for _model, spec in self._builders.items():
            aliases[f'{spec.get_type().__module__}.{spec.get_type().__name__}'] = spec
        self._builders.update(aliases)

    def create(self, key, fallback=None, **kwargs) -> Experiment:  # noqa: F821
        """
        Create an experiment of type key.

        Args:
            key: Experiment Type
            fallback: Fallback type. If none, uses DEFAULT_KEY
            **kwargs: Options to pass to the experiment object

        Returns:
            Experiment object that was created
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Attempting to create experiment of type {key}")

        if not key:
            key = self.DEFAULT_KEY
        else:
            logger.warning(f'Experiment type: {key}')

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
