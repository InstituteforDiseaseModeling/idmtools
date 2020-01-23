from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any, Tuple, List, Dict, NoReturn
from uuid import UUID

from idmtools.core import CacheEnabled
from idmtools.entities import ISimulation


@dataclass
class IPlatformSimulationOperations(CacheEnabled, ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, simulation_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an Simulation

        Args:
            simulation_id: Item id of Simulations
            **kwargs:

        Returns:
            Platform Representation of an simulation
        """
        pass

    def pre_create(self, simulation: ISimulation, **kwargs) -> NoReturn:
        """
        Run the platform/simulation post creation events

        Args:
            simulation: simulation to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        simulation.pre_creation()

    def post_create(self, simulation: ISimulation, **kwargs) -> NoReturn:
        """
        Run the platform/simulation post creation events

        Args:
            simulation: simulation to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        simulation.post_creation()

    def create(self, simulation: ISimulation, do_pre: bool = True, do_post: bool = True, **kwargs):
        """
        Creates an simulation from an IDMTools simulation object. Also performs pre-creation and post-creation
        locally and on platform

        Args:
            simulation: Simulation to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        if do_pre:
            self.pre_create(simulation, **kwargs)
        ret = self.platform_create(simulation, **kwargs)
        if do_post:
            self.post_create(simulation, **kwargs)
        return ret

    @abstractmethod
    def platform_create(self, simulation: ISimulation, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an simulation on Platform from an IDMTools Simulation Object

        Args:
            simulation: Simulation to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    def batch_create(self, sims: List[ISimulation], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create simulations

        Args:
            sims: List of simulations to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for sim in sims:
            ret.append(self.create(sim, **kwargs))
        return ret

    @abstractmethod
    def get_parent(self, simulation: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            simulation:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    def to_entity(self, simulation: Any, **kwargs) -> ISimulation:
        """
        Converts the platform representation of simulation to idmtools representation

        Args:
            simulation:Platform simulation object

        Returns:
            IDMTools simulation object
        """
        return simulation

    @abstractmethod
    def run_item(self, simulation: ISimulation):
        """
        Called during commissioning of an item. This should create the remote resource but not upload assets

        Args:
            simulation: Simulation to run

        Returns:

        """
        pass

    @abstractmethod
    def send_assets(self, simulation: Any):
        pass

    @abstractmethod
    def refresh_status(self, simulation: ISimulation):
        """
        Refresh status for simulation object

        Args:
            simulation: Experiment to get status for

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_assets(self, simulation: ISimulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get files from simulation

        Args:
            simulation: Simulation to fetch files from
            files: Files to get
            **kwargs:

        Returns:
            Dictionary containting filename and content
        """
        pass

    @abstractmethod
    def list_assets(self, simulation: ISimulation) -> List[str]:
        """
        List available files for a simulation

        Args:
            simulation: Simulation to list files for

        Returns:
            List of filenames
        """
        pass