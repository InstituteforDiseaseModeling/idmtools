from abc import ABCMeta, abstractmethod

from interfaces.IExperiment import IExperiment
from interfaces.ISimulation import ISimulation
from utils.decorators import abstractstatic


class IPlatform(metaclass=ABCMeta):
    """
    Interface defining a platform.
    A platform needs to implement basic operation such as:
    - Creating experiment
    - Creating simulation
    - Commissioning
    - File handling
    """

    @abstractstatic
    def create_experiment(experiment: IExperiment):
        """
        Function creating an experiment on the platform.
        Args:
            experiment: The experiment to create
        """
        pass

    @abstractstatic
    def create_simulation(simulation: ISimulation):
        """
        Function creating a simulation on the platform for a given experiment.
        Args:
            simulation: The simulation to create
        """
        pass

    @abstractstatic
    def run_simulation(simulation):
        """
        Run a given simulation on the platform
        Args:
            simulation: The simulation to run
        """
        pass