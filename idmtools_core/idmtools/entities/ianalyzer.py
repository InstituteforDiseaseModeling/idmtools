"""
Defines our IAnalyzer interface used as base of all other analyzers.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABCMeta, abstractmethod
from logging import getLogger
from typing import Any, NoReturn, List, TypeVar, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from idmtools.core.interfaces.iitem import IItemList
    from idmtools.entities.iworkflow_item import IWorkflowItem
    from idmtools.entities.simulation import Simulation

logger = getLogger(__name__)
# Items that we support analysis on
ANALYZABLE_ITEM = Union['IWorkflowItem', 'Simulation']
# The item type we pass to analysis
ANALYSIS_ITEM_MAP_DATA_TYPE = Dict[str, Any]
# The datatype if the reduce input
ANALYSIS_REDUCE_DATA_TYPE = Dict[ANALYZABLE_ITEM, Any]


class IAnalyzer(metaclass=ABCMeta):
    """
    An abstract base class carrying the lowest level analyzer interfaces called by :class:`~idmtools.managers.experiment_manager.ExperimentManager`.
    """

    @abstractmethod
    def __init__(self, uid=None, working_dir: Optional[str] = None, parse: bool = True, filenames: Optional[List[str]] = None):
        """
        A constructor.

        Args:
            uid: The unique id identifying this analyzer.
            working_dir: A working directory to place files.
            parse: True to leverage the :class:`OutputParser`; False to get the raw
                data in the :meth:`select_simulation_data`.
            filenames: The files for the analyzer to download.
        """
        self.parse = parse
        self.working_dir = working_dir
        self.uid = uid or self.__class__.__name__
        self.results = None  # Store what finalize() is returning
        self._filenames = filenames or list()
        self._filenames = [f.replace("\\", '/') for f in self._filenames]

    @property
    def filenames(self):
        """
        Returns user filenames.

        Returns:
            filenames

        """
        return self._filenames

    @filenames.setter
    def filenames(self, value):
        """
        Set the filenames property.

        Args:
            value: new filenames

        Returns:
            None

        """
        self._filenames = value or list()
        self._filenames = [f.replace("\\", '/') for f in self._filenames]

    def initialize(self) -> NoReturn:
        """
        Call once after the analyzer has been added to the :class:`~idmtools.analysis.AnalyzeManager`.

        Add everything depending on the working directory or unique ID here instead of in __init__.
        """
        pass

    def per_group(self, items: 'IItemList') -> NoReturn:
        """
        Call once before running the apply on the items.

        Args:
            items: Objects with attributes of type :class:`~idmtools.core.item_id.ItemId`. IDs of one or
                more higher-level hierarchical objects can be obtained from these IDs in order to perform
                tasks with them.

        Returns:
            None
        """
        pass

    def filter(self, item: ANALYZABLE_ITEM) -> bool:
        """
        Decide whether the analyzer should process a simulation/work item.

        Args:
            item: An :class:`~idmtools.entities.iitem.IItem` to be considered for processing with this analyzer.

        Returns:
            A Boolean indicating whether simulation/work item should be analyzed by this analyzer.
        """
        return True

    @abstractmethod
    def map(self, data: ANALYSIS_ITEM_MAP_DATA_TYPE, item: ANALYZABLE_ITEM) -> Any:
        """
        In parallel for each simulation/work item, consume raw data from filenames and emit selected data.

        Args:
            data: A dictionary associating filename with content for simulation data.
            item: :class:`~idmtools.entities.iitem.IItem` object that the passed data is associated with.

        Returns:
            Selected data for the given simulation/work item.
        """
        return None

    @abstractmethod
    def reduce(self, all_data: ANALYSIS_REDUCE_DATA_TYPE) -> Any:
        """
        Combine the :meth:`map` data for a set of items into an aggregate result.

        Args:
            all_data: A dictionary with entries for the item ID and selected data.
        """
        pass

    def destroy(self) -> NoReturn:
        """
        Call after the analysis is done.
        """
        pass


# Alias IAnalyzer for computability with old code but print a deprecation warning

class BaseAnalyzer(IAnalyzer, metaclass=ABCMeta):
    """
    BaseAnalyzer to allow using previously used dtk-tools analyzers within idmtools.
    """

    def __init__(self, uid=None, working_dir: Optional[str] = None, parse: bool = True, filenames: Optional[List[str]] = None):
        """
        Constructor for Base Analyzer.

        Args:
            uid: The unique id identifying this analyzer.
            working_dir: A working directory to place files.
            parse: True to leverage the :class:`OutputParser`; False to get the raw
                data in the :meth:`select_simulation_data`.
            filenames: The files for the analyzer to download.
        """
        logger.warning('Base analyzer name will soon be deprecated in favor of IAnalyzer')
        # TODO: Make transition documentation so we can deprecat this
        super().__init__(uid, working_dir, parse, filenames)


TAnalyzer = TypeVar("TAnalyzer", bound=IAnalyzer)
TAnalyzerList = List[TAnalyzer]
