from abc import ABCMeta, abstractmethod
import typing

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TAllSimulationData
    from typing import Any


class IAnalyzer(metaclass=ABCMeta):
    """
    An abstract base class carrying the lowest level analyzer interfaces called by :class:`BaseExperimentManager`.
    """

    @abstractmethod
    def __init__(self, uid=None, working_dir=None, parse=True, filenames=None):
        """
        A constructor.

        Args:
            uid: The unique ID identifying this analyzer.
            working_dir: A working directory to dump files.
            parse: True to leverage the :class:`OutputParser`; 
                False to get raw data in the :meth:`select_simulation_data`.
            filenames: The files the analyzer needs to download.
        """
        self.filenames = filenames or []
        self.parse = parse
        self.working_dir = working_dir
        self.uid = uid or self.__class__.__name__
        self.results = None  # Store what finalize() is returning

    def initialize(self):
        """
        Called once after the analyzer has been added to the :class:`idmtools.managers.AnalyzeManager`.
        Place everything depending on the working directory here instead of in :meth:`__init__`.
        """
        pass

    def per_experiment(self, experiment: 'TExperiment') -> None:
        """
        Call once per experiment before applying the analyzer on the simulations.

        Args:
            experiment: Called for each experiment.
        """
        pass

    def filter(self, simulation: 'TSimulation') -> bool:
        """
        Indicate the simulation for the analyzer to process. 

        Args:
            simulation: The simulation object.

        Returns:
            A Boolean indicating whether the simulation should be analyzed by this analyzer.
        """
        return True

    def select_simulation_data(self, data: 'Any', simulation: 'TSimulation') -> 'Any':
        """
        In parallel for each simulation, consume raw data from filenames and emit selected data.

        Args:
            data: Simulation data in a dictionary associating filename with content.
            simulation: Object representing the simulation for which the data is passed.

        Returns: 
            Selected data for the given simulation.
        """
        return None

    def finalize(self, all_data: 'TAllSimulationData') -> 'Any':
        """
        On a single process, get all the selected data.

        Args:
            all_data: Dictionary associating simulation and selected data.
        """
        pass

    def destroy(self):
        """
        Delete objects after the analysis is done.
        """
        pass
