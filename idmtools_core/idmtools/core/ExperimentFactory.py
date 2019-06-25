import typing

if typing.TYPE_CHECKING:
    from idmtools.core import TExperimentClass, TExperiment


class ExperimentFactory:
    def __init__(self):
        self._builders = {}

    def register_type(self, experiment_class: 'TExperimentClass'):
        self._builders[experiment_class.__name__] = experiment_class

    def create(self, key, **kwargs) -> 'TExperiment':
        builder = self._builders.get(key)
        if not builder:
            raise ValueError(key)
        return builder(**kwargs)


experiment_factory = ExperimentFactory()
