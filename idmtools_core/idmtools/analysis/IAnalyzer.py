from abc import ABCMeta, abstractmethod
import typing

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TAllSimulationData
    from typing import Any


class IAnalyzer(metaclass=ABCMeta):
    """
    An abstract base class carrying the lowest level analyzer interfaces called by 
    :class:`~idmtools.managers.ExperimentManager.ExperimentManager`.
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

    def initialize(self):
        """
        Call once after the analyzer has been added to the :class:`~idmtools.managers.AnalyzeManager`.

        Add everything depending on the working directory or unique ID here instead of in __init__.
        """
        pass

    def per_experiment(self, experiment: 'TExperiment') -> None:
        """
        Call once per experiment before doing the apply on the simulations.

        Args:
            experiment: The experiment ID.
        """
        pass

    def filter(self, simulation: 'TSimulation') -> bool:
        """
        Decide whether analyzer should process a simulation.

        Args:
            simulation: The simulation object.

        Returns:
            Boolean indicating whether simulation should be analyzed by this analyzer.
        """
        return True

    def select_simulation_data(self, data: 'Any', simulation: 'TSimulation') -> 'Any':
        """
        In parallel for each simulation, consume raw data from filenames and emit selected data.

        Args:
            data: The simulation data, a dictionary associating filename with content.
            simulation: An object representing the simulation for which the data is passed.

        Returns: 
            The selected data for the given simulation.
        """
        return None

    def finalize(self, all_data: 'TAllSimulationData') -> 'Any':
        """
        On a single process, get all the selected data.

        Args:
            all_data: A dictionary associating simulation and selected data.
        """
        pass

    def destroy(self):
        """
        Call after the analysis is done.
        """
        pass
