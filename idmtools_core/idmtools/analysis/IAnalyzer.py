from abc import ABCMeta, abstractmethod
import typing

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TAllSimulationData
    from typing import Any


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

    def initialize(self):
        """
        Called once after the analyzer has been added to the AnalyzeManager.
        Everything depending on the working directory or uid should be here instead of in __init__
        """
        pass

    def per_group(self, items: 'Any') -> None:
        """
        Called once before running the apply on the simulations.
        Args:
            items: objects with 'full_id' attributes of type ItemId. Ids of one or more higher-level hierarchical
                   objects can be obtained from these full_ids in order to perform tasks with them.
        """
        pass

    def filter(self, item: 'Any') -> bool:
        """
        Decide whether analyzer should process a simulation
        Args:
            simulation: simulation object

        Returns:Boolean whether simulation should be analyzed by this analyzer
        """
        return True

    def map(self, data: 'Any', item: 'Any') -> 'Any':
        """
        In parallel for each simulation, consume raw data from filenames and emit selected data
        Args:
            data: simulation data. Dictionary associating filename with content
            simulation: object representing the simulation for which the data is passed

        Returns: selected data for the given simulation
        """
        return None

    def reduce(self, all_data: 'Any') -> 'Any':
        """
        On a single process, get all the selected data
        Args:
            all_data: dictionary associating simulation:selected_data
        """
        pass

    def destroy(self):
        """
        Called after the analysis is done
        """
        pass
