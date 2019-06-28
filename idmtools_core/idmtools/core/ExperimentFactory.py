import typing

if typing.TYPE_CHECKING:
    from idmtools.core import TExperimentClass, TExperiment


class ExperimentFactory:
    def __init__(self):
        self._builders = {}

    def register_type(self, experiment_class: 'TExperimentClass'):
        self._builders[experiment_class.__module__] = experiment_class

    def create(self, key, **kwargs) -> 'TExperiment':
        if key not in self._builders:
            try:
                # Try first to import it dynamically
                import importlib
                importlib.import_module(key)
            except:
                raise ValueError(f"The ExperimentFactory could not create an experiment of type {key}")

        builder = self._builders.get(key)
        return builder(**kwargs)


experiment_factory = ExperimentFactory()
