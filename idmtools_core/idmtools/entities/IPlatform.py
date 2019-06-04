import typing
from abc import ABCMeta, abstractmethod

from idmtools.core import IEntity

if typing.TYPE_CHECKING:
    from idmtools.core.types import TExperiment, TSimulation, TAssetCollection


class IPlatform(IEntity, metaclass=ABCMeta):
    """
    Interface defining a platform.
    A platform needs to implement basic operation such as:
    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """

    @abstractmethod
    def create_experiment(self, experiment: 'TExperiment'):
        """
        Function creating an experiment on the platform.
        Args:
            experiment: The experiment to create
        """
        pass

    @abstractmethod
    def create_simulations(self, experiment: 'TExperiment'):
        """
        Function creating experiments simulations on the platform for a given experiment.
        Args:
            experiment: The experiment containing the simulations to create
        """
        pass

    @abstractmethod
    def run_simulations(self, experiment: 'TExperiment'):
        """
        Run the simulations for a given experiment on the platform
        Args:
            experiment: The experiment to run
        """
        pass

    @abstractmethod
    def send_assets_for_experiment(self, experiment: 'TExperiment'):
        pass

    @abstractmethod
    def send_assets_for_simulation(self, simulation: 'TSimulation', assets:'TAssetCollection'):
        pass