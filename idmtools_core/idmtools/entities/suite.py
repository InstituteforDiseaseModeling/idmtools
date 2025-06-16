"""
Defines our Suite object.

The Suite object can be thought as a metadata object. It represents a container object for Experiments. All Suites should have one or more experiments.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import NoReturn, Type, TYPE_CHECKING, Dict
from abc import ABC
from dataclasses import dataclass, field, fields
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core import ItemType, EntityContainer, UnknownItemException
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.experiment import Experiment


@dataclass(repr=False)
class Suite(INamedEntity, ABC, IRunnableEntity):
    """
    Class that represents a generic suite (a collection of experiments).

    Args:
        experiments: The child items of this suite.
    """
    _experiments: EntityContainer = field(
        default_factory=lambda: EntityContainer(),
        compare=False,
        metadata={"pickle_ignore": True}
    )

    item_type: ItemType = field(default=ItemType.SUITE, compare=False, init=False)
    description: str = field(default=None, compare=False)

    def add_experiment(self, experiment: 'Experiment') -> 'NoReturn':  # noqa: F821
        """
        Add an experiment to the suite.

        Args:
            experiment: the experiment to be linked to suite
        """
        ids = [exp.uid for exp in self._experiments or []]
        if experiment.uid in ids:
            return

        # Link the suite to the experiment. Assumes the experiment suite setter adds the experiment to the suite.
        experiment.suite = self

    def display(self):
        """
        Display workflowitem.

        Returns:
            None
        """
        from idmtools.utils.display import display, suite_table_display
        display(self, suite_table_display)

    def pre_creation(self, platform: 'IPlatform'):
        """
        Pre Creation of IWorkflowItem.

        Args:
            platform: Platform we are creating item on

        Returns:
            None
        """
        IItem.pre_creation(self, platform)

    def post_creation(self, platform: 'IPlatform'):
        """
        Post Creation of IWorkflowItem.

        Args:
            platform: Platform

        Returns:
            None
        """
        IItem.post_creation(self, platform)

    def __repr__(self):
        """
        String representation of suite.
        """
        num_experiments = len(self._experiments or [])
        return f"<Suite {self.uid} - {num_experiments} experiments>"

    @property
    def done(self):
        """
        Return if a suite has finished executing.

        Returns:
            True if all experiments have ran, False otherwise
        """
        return all([s.done for s in self.experiments])

    @property
    def succeeded(self) -> bool:
        """
        Return if a suite has succeeded. A suite is succeeded when all experiments have succeeded.

        Returns:
            True if all experiments have succeeded, False otherwise
        """
        return all([s.succeeded for s in self.experiments])

    def to_dict(self) -> Dict:
        """
        Converts suite to a dictionary.

        Returns:
            Dictionary of suite.
        """
        result = dict()
        for f in fields(self):
            if not f.name.startswith("_") and f.name not in ['parent']:
                result[f.name] = getattr(self, f.name)
        result['_uid'] = self.uid
        return result

    @property
    def experiments(self) -> EntityContainer:
        """
        Access the list of experiments in this suite.

        If experiments are not yet loaded, it will fetch them from the platform.

        Returns:
            EntityContainer: A container of Experiment objects.
        """
        if self._experiments is None:
            self._experiments = self.get_experiments()
        return self._experiments

    @experiments.setter
    def experiments(self, value):
        """
        Set the list of experiments for the suite.
        Args:
            value (EntityContainer): The list of experiments to assign.
        """
        self._experiments = value

    def get_experiments(self):
        """
        Retrieve the experiments associated with this suite from the platform.
        Returns:
            EntityContainer: A container of Experiment objects belonging to this suite.
        """
        if self.platform:
            return self.platform.get_children(self.uid, ItemType.SUITE)
        else:
            raise UnknownItemException(f"Suite {self.id} cannot retrieve experiments because it was not found on the platform.")


ISuiteClass = Type[Suite]
