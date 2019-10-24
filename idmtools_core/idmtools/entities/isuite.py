import typing
from abc import ABC
from dataclasses import dataclass, field
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core import ItemType, EntityContainer


@dataclass(repr=False)
class ISuite(INamedEntity, ABC):
    """
    Represents a generic Suite (of experiments).

    Args:
        experiments: the children items of this suite
    """
    experiments: 'EntityContainer' = field(default_factory=lambda: EntityContainer(), compare=False,
                                           metadata={"pickle_ignore": True})

    item_type: 'ItemType' = field(default=ItemType.SUITE, compare=False, init=False)

    def add_experiment(self, experiment):
        self.experiments.append(experiment)


TSuite = typing.TypeVar("TSuite", bound=ISuite)
TSuiteClass = typing.Type[TSuite]
