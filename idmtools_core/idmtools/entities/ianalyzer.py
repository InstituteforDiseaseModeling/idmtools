import typing

from abc import ABCMeta, abstractmethod
from typing import Any, NoReturn

if typing.TYPE_CHECKING:
    from idmtools.core.interfaces.iitem import TItem, TItemList


class IAnalyzer(metaclass=ABCMeta):
    """
    An abstract base class carrying the lowest level analyzer interfaces called by BaseExperimentManager
    """

    @abstractmethod
    def __init__(self, uid=None, working_dir=None, parse=True, filenames=None):
        """
        Constructor
        Args:
            uid: The unique id identifying this analyzer
            working_dir: A working directory to dump files
            parse: Do we want to leverage the OutputParser or just get the raw data in the map()
            filenames: Which files the analyzer needs to download
        """
        self.filenames = filenames or []
        self.parse = parse
        self.working_dir = working_dir
        self.uid = uid or self.__class__.__name__
        self.results = None  # Store what finalize() is returning

    def initialize(self) -> NoReturn:
        """
        Called once after the analyzer has been added to the AnalyzeManager.
        Everything depending on the working directory or uid should be here instead of in __init__
        """
        pass

    def per_group(self, items: 'TItemList') -> NoReturn:
        """
        Called once before running the apply on the simulations.
        Args:
            items: objects with 'full_id' attributes of type ItemId. Ids of one or more higher-level hierarchical
                   objects can be obtained from these full_ids in order to perform tasks with them.
        """
        pass

    def filter(self, item: 'TItem') -> bool:
        """
        Decide whether analyzer should process a simulation
        Args:
            item: an IItem to be considered for processing with this analyzer

        Returns: Boolean (True/False) whether the item should be analyzed by this analyzer
        """
        return True

    def map(self, data: 'Any', item: 'TItem') -> 'Any':
        """
        In parallel for each simulation, consume raw data from filenames and emit selected data
        Args:
            data: simulation data. Dictionary associating filename with content
            item: IItem object that the passed data is associated with

        Returns: selected data for the given item
        """
        return None

    def reduce(self, all_data: dict) -> 'Any':
        """
        Combine the map() data for a set of items into an aggregate result.
        Args:
            all_data: dictionary with entries:    item_id: selected_data
        """
        pass

    def destroy(self) -> NoReturn:
        """
        Called after the analysis is done
        """
        pass


TAnalyzer = typing.TypeVar("TAnalyzer", bound=IAnalyzer)
TAnalyzerList = typing.List[TAnalyzer]
