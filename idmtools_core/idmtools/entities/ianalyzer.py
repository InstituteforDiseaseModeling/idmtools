import typing

from abc import ABCMeta, abstractmethod
from typing import Any, NoReturn

if typing.TYPE_CHECKING:
    from idmtools.core.interfaces.iitem import TItem, TItemList


class IAnalyzer(metaclass=ABCMeta):
    """
    An abstract base class carrying the lowest level analyzer interfaces called by
     :class:`~idmtools.managers.experiment_manager.ExperimentManager`.
    """

    @abstractmethod
    def __init__(self, uid=None, working_dir=None, parse=True, filenames=None):
        """
        A constructor.

        Args:
            uid: The unique id identifying this analyzer.
            working_dir: A working directory to place files.
            parse: True to leverage the :class:`OutputParser`; False to get the raw
                data in the :meth:`select_simulation_data`.
            filenames: The files for the analyzer to download.
        """
        self.filenames = filenames or []
        self.parse = parse
        self.working_dir = working_dir
        self.uid = uid or self.__class__.__name__
        self.results = None  # Store what finalize() is returning

    def initialize(self) -> NoReturn:
        """
        Call once after the analyzer has been added to the :class:`~idmtools.analysis.AnalyzeManager`.

        Add everything depending on the working directory or unique ID here instead of in __init__.
        """
        pass

    def per_group(self, items: 'TItemList') -> NoReturn:
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

    def filter(self, item: 'TItem') -> bool:
        """
        Decide whether the analyzer should process a simulation.

        Args:
            item: An :class:`~idmtools.entities.iitem.IItem` to be considered for processing with this analyzer.

        Returns:
            A Boolean indicating whether simulation should be analyzed by this analyzer.
        """
        return True

    @abstractmethod
    def map(self, data: 'Any', item: 'TItem') -> 'Any':
        """
        In parallel for each simulation, consume raw data from filenames and emit selected data.

        Args:
            data: A dictionary associating filename with content for simulation data.
            item: :class:`~idmtools.entities.iitem.IItem` object that the passed data is associated with.

        Returns:
            Selected data for the given item.
        """
        return None

    @abstractmethod
    def reduce(self, all_data: dict) -> 'Any':
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


TAnalyzer = typing.TypeVar("TAnalyzer", bound=IAnalyzer)
TAnalyzerList = typing.List[TAnalyzer]
