import typing
from logging import getLogger

if typing.TYPE_CHECKING:
    from idmtools.core import TExperimentClass, TExperiment


logger = getLogger(__name__)


class ExperimentFactory:

    DEFAULT_KEY = 'idmtools_models.dtk.DTKExperiment'

    def __init__(self):
        self._builders = {}

    def register_type(self, experiment_class: 'TExperimentClass'):
        self._builders[experiment_class.__module__] = experiment_class

    def create(self, key, platform, **kwargs) -> 'TExperiment':
        if key is None:
            key = self.DEFAULT_KEY
            logger.warning(f'No experiment type tag found, assuming type: {key}')

        if key not in self._builders:
            try:
                # Try first to import it dynamically
                import importlib
                importlib.import_module(key)
            except Exception as e:
                logger.exception(e)
                raise ValueError(f"The ExperimentFactory could not create an experiment of type {key}")

        builder = self._builders.get(key)
        experiment = builder(**kwargs)
        experiment.platform = platform
        return experiment


experiment_factory = ExperimentFactory()
