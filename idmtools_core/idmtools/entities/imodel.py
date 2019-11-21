from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from idmtools.assets import Asset
from idmtools.entities.itask import ITask


@dataclass
class IModel(ITask, ABC):
    @abstractmethod
    def gather_experiment_assets(self) -> List[Asset]:
        """
        Gather list of experiment level assets. For models, this should be your common files like binaries, etc

        Returns:
            List of Assets
        """
        pass

    @abstractmethod
    def pre_experiment_creation(self):
        """
        Hook called just before a platform creates an experiment containing a set of simulations using the model
        Returns:

        """
        pass

    @abstractmethod
    def pre_simulation_creation(self):
        """
        Hooke called just before a platform creates a simulation running said model
        Returns:

        """
        pass

    @abstractmethod
    def set_parameter(self, *args, **kwargs):
        """
        Requires to make use of sweep tools. Allows sweep tools(or users) to set parameters in model. The definition
           is loose to allow many possible config models
        Args:
            *args:
            **kwargs:

        Returns:

        """
        pass

    @abstractmethod
    def get_parameter(self, *args, **kwargs):
        """
        Requires to make use of sweep tools. Allows sweep tools(or users) to get parameters in model. The definition
           is loose to allow many possible config models
        Args:
            *args:
            **kwargs:

        Returns:

        """
        pass
