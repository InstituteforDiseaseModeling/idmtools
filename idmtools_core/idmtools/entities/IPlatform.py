import uuid
import typing
from abc import ABCMeta, abstractmethod
from logging import getLogger
from idmtools.core.interfaces.IEntity import IEntity

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TSimulationBatch
    from typing import List, Dict, Any

logger = getLogger(__name__)

CALLER_LIST = ['_create_from_block',    # create platform through Platform Factory
               'fetch',                 # create platform through un-pickle
               'get'                    # create platform through platform spec' get method
               ]


class IPlatform(IEntity, metaclass=ABCMeta):
    """
    Interface defining a platform.
    A platform needs to implement basic operation such as:
    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """

    @staticmethod
    def get_caller():
        import inspect

        s = inspect.stack()
        return s[2][3]

    def __new__(cls, *args, **kwargs):
        """
        Here is the code to create a new object!
        Args:
            *args: user inputs
            **kwargs: user inputs
        Returns: object created
        """

        # Check the caller
        caller = cls.get_caller()

        # Action based on the called
        if caller in CALLER_LIST:
            return super().__new__(cls)
        else:
            raise ValueError(
                f"Please use Factory to create Platform! For example: platform = Platform('COMPS', **kwargs)")

    def __post_init__(self) -> None:
        """
        Work to be done after object creation
        Returns: None
        """
        pass

    @abstractmethod
    def create_experiment(self, experiment: 'TExperiment') -> None:
        """
        Function creating an experiment on the platform.
        Args:
            experiment: The experiment to create
        """
        pass

    @abstractmethod
    def create_simulations(self, simulation_batch: 'TSimulationBatch') -> 'List[Any]':
        """
        Function creating experiments simulations on the platform for a given experiment.
        Args:
            simulation_batch: The batch of simulations to create
        Returns:
            List of ids created
        """
        pass

    @abstractmethod
    def run_simulations(self, experiment: 'TExperiment') -> None:
        """
        Run the simulations for a given experiment on the platform
        Args:
            experiment: The experiment to run
        """
        pass

    @abstractmethod
    def send_assets_for_experiment(self, experiment: 'TExperiment', **kwargs) -> None:
        """
        Send the assets for a given experiment to the platform.
        Args:
            experiment: The experiment to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def send_assets_for_simulation(self, simulation: 'TSimulation', **kwargs) -> None:
        """
        Send the assets for a given simulation to the platform.
        Args:
            simulation: The simulation to process. Expected to have an `assets` attribute containing the collection.
            **kwargs: Extra parameters used by the platform
        """
        pass

    @abstractmethod
    def refresh_experiment_status(self, experiment: 'TExperiment') -> None:
        """
        Populate the experiment and its simulations with status.
        Args:
            experiment: The experiment to check status for
        """
        pass

    @abstractmethod
    def restore_simulations(self, experiment: 'TExperiment') -> None:
        """
        Populate the experiment with the associated simulations.
        Args:
            experiment: The experiment to populate
        """
        pass

    @abstractmethod
    def get_assets_for_simulation(self, simulation: 'TSimulation', output_files: 'List[str]') -> 'Dict[str, bytearray]':
        pass

    @abstractmethod
    def retrieve_experiment(self, experiment_id: 'uuid') -> 'TExperiment':
        pass

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"
