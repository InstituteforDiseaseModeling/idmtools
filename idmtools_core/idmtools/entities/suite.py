"""
Defines our Suite object.

The Suite object can be thought as a metadata object. It represents a container object for Experiments. All Suites should have one or more experiments.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import NoReturn, Type, TYPE_CHECKING, Dict, List
from abc import ABC
from dataclasses import dataclass, field, fields

from idmtools.assets import Asset
from idmtools.core.interfaces.iitem import IItem
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.core import ItemType, EntityContainer
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.utils.filters.asset_filters import TFILE_FILTER_TYPE

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform
    from idmtools.entities.experiment import Experiment
    from idmtools.entities.simulation import Simulation


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
        Add an experiment to the suite.

        Args:
            experiment: the experiment to be linked to suite
        """
        ids = [exp.uid for exp in self.experiments]
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
        return f"<Suite {self.uid} - {len(self.experiments)} experiments>"

    @property
    def done(self):
        """
        Return if an suite has finished executing.

        Returns:
            True if all experiments have ran, False otherwise
        """
        return all([s.done for s in self.experiments])

    @property
    def succeeded(self) -> bool:
        """
        Return if an suite has succeeded. An suite is succeeded when all experiments have succeeded.

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

    def list_assets(self, children: bool = False, platform: 'IPlatform' = None, filters: TFILE_FILTER_TYPE = None, **kwargs) -> List[Asset]:
        """
        List assets that have been uploaded to a server already.

        Args:
            children: When set to true, simulation assets will be loaded as well
            filters: Filters to apply. These should be a function that takes a str and return true or false
            platform: Optional platform to load assets list from
            **kwargs:

        Returns:
            List of assets
        """
        if self.id is None:
            raise ValueError("You can only list static assets on an existing experiment")
        p = super()._check_for_platform_from_context(platform)
        return p.list_assets(self, children=children, filters=filters, **kwargs)

    def list_files(self, platform: 'IPlatform' = None, filters: TFILE_FILTER_TYPE = None, **kwargs) -> List[Asset]:
        """
        List files for suite.

        Args:
            platform: Optional platform to load assets list from
            filters: Filters to apply. These should be a function that takes a str and return true or false
            **kwargs:

        Returns:
            List of assets
        """
        if self.id is None:
            raise ValueError("You can only list static assets on an existing experiment")
        p = super()._check_for_platform_from_context(platform)
        return p.list_files(self, filters=filters, **kwargs)

    def list_children_files(self, platform: 'IPlatform' = None, filters: TFILE_FILTER_TYPE = None, **kwargs) -> Dict['Experiment', Dict['Simulation', List[Asset]]]:
        """
        List Children Files.

        Args:
            platform: Optional platform to load assets list from
            filters: Filters to apply. These should be a function that takes a str and return true or false
            **kwargs:

        Returns:
            Dictionary of Simulation -> List of Assets
        """
        if self.id is None:
            raise ValueError("You can only list static assets on an existing experiment")
        p = super()._check_for_platform_from_context(platform)
        return p.list_children_files(self, filters=filters, **kwargs)


ISuiteClass = Type[Suite]
