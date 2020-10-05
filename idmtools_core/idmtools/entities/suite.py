from typing import NoReturn, Type, TYPE_CHECKING, Dict
from abc import ABC
from dataclasses import dataclass, field, fields
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core import ItemType, EntityContainer, EntityStatus
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity

if TYPE_CHECKING:
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.experiment import Experiment


@dataclass(repr=False)
class Suite(INamedEntity, ABC, IRunnableEntity):
    """
    Class that represents a generic suite (a collection of experiments).

    Args:
        experiments: The child items of this suite.
    """
    experiments: EntityContainer = field(
        default_factory=lambda: EntityContainer(),
        compare=False,
        metadata={"pickle_ignore": True}
    )

    item_type: ItemType = field(default=ItemType.SUITE, compare=False, init=False)
    description: str = field(default=None, compare=False)

    def add_experiment(self, experiment: 'Experiment') -> 'NoReturn':  # noqa: F821
        """
        Add an experiment to the suite
        Args:
            experiment: the experiment to be linked to suite
        """
        ids = [exp.uid for exp in self.experiments]
        if experiment.uid in ids:
            return

        # Link the suite to the experiment. Assumes the experiment suite setter adds the experiment to the suite.
        experiment.suite = self

    def display(self):
        from idmtools.utils.display import display, suite_table_display
        display(self, suite_table_display)

    def pre_creation(self, platform: 'IPlatform'):
        IItem.pre_creation(self, platform)

    def post_creation(self, platform: 'IPlatform'):
        IItem.post_creation(self, platform)

    def __repr__(self):
        return f"<Suite {self.uid} - {len(self.experiments)} experiments>"

    @property
    def done(self):
        """
        Return if an suite has finished executing

        Returns:
            True if all experiments have ran, False otherwise
        """
        return all([s.done for s in self.experiments])

    @property
    def succeeded(self) -> bool:
        """
        Return if an suite has succeeded. An suite is succeeded when all experiments have succeeded

        Returns:
            True if all experiments have succeeded, False otherwise
        """
        return all([s.succeeded for s in self.experiments])

    def to_dict(self) -> Dict:
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)
        result['_uid'] = self.uid
        return result


ISuiteClass = Type[Suite]
