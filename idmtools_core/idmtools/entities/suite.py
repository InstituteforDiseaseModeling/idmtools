"""
Defines our Suite object.

The Suite object can be thought as a metadata object. It represents a container object for Experiments. All Suites should have one or more experiments.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import NoReturn, Type, TYPE_CHECKING, Dict, List
from abc import ABC
from dataclasses import dataclass, field, fields
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core import ItemType, EntityContainer
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
    experiments: EntityContainer = field(
        default_factory=lambda: EntityContainer(),
        compare=False,
        metadata={"pickle_ignore": True}
    )

    item_type: ItemType = field(default=ItemType.SUITE, compare=False, init=False)
    description: str = field(default=None, compare=False)

    def __post_init__(self):
        """
        Initialize Suite.
        """
        self.experiments = EntityContainer()

    def add_experiment(self, experiment: 'Experiment') -> 'NoReturn':  # noqa: F821
        """
        Add an experiment to the suite.

        Args:
            experiment: the experiment to be linked to suite
        """
        ids = [exp.uid for exp in self.experiments]
        if experiment.uid in ids:
            return

        # Link the suite to the experiment. Assumes the experiment suite setter adds the experiment to the suite.
        experiment._parent = self
        experiment.parent_id = experiment.suite_id = self.id

        # add experiment
        self.experiments.append(experiment)

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
        count = len(self.experiments) if self.experiments is not None else 0
        return f"<Suite {self.uid} - {count} experiments>"

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

    def get_experiments(self) -> EntityContainer:
        """
        Retrieve the experiments associated with this suite from the platform.
        Returns:
            EntityContainer: A container of Experiment objects belonging to this suite.
        """
        experiments = self.experiments
        if not experiments:
            experiments = self.platform.get_children(self.id, ItemType.SUITE, force=True)
        return experiments

    def get_simulations_by_tags(self, tags=None, status=None, entity_type=False, skip_sims=None, max_simulations=None,
                                **kwargs) -> Dict[str, List[str]]:
        """
        Retrieve simulation ids or simulation objects with matching tags across all experiments in the suite.
        This method filters simulations based on the provided tags, skipping specified simulations,
        and limiting the number of results if `max_simulations` is set. The return type can be
        either a dictionary of simulation IDs or simulation objects, depending on the `entity_type` flag.
        Args:
            status:
            tags (dict, optional): A simulation's tags to filter by.
            status (EntityStatus, Optional): Simulation status.
            entity_type (bool, optional): If True, return simulation objects; otherwise, return simulation IDs. Defaults to False.
            skip_sims (List[str], optional): A list of simulation IDs to exclude from the results.
            max_simulations (int, optional): The maximum number of simulations to return per experiment.
            **kwargs: Additional filter parameters.
        Returns:
            Dict[str, List[str]]: A dictionary where the keys are experiment IDs and the values are lists of
                                  simulation IDs or simulation objects, depending on the `entity_type` flag.
        """
        experiments = self.get_experiments()
        sims = {}
        for experiment in experiments:
            sims[experiment.id] = experiment.get_simulations_by_tags(tags=tags, status=status, entity_type=entity_type,
                                                                     skip_sims=skip_sims,
                                                                     max_simulations=max_simulations, **kwargs)
        return sims

    def __setstate__(self, state):
        """
        Add ignored fields back since they don't exist in the pickle.
        """
        # First call parent's __setstate__ to restore base attributes
        super().__setstate__(state)
        # Restore the pickle fields with values requested
        self.experiments = EntityContainer()


ISuiteClass = Type[Suite]
