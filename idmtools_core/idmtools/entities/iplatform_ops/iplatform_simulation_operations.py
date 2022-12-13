"""
IPlatformSimulationOperations defines simulation item operations interface.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import getLogger, DEBUG
from typing import Type, Any, List, Dict, NoReturn, Optional
from idmtools.assets import Asset
from idmtools.core.cache_enabled import CacheEnabled
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform_ops.utils import batch_create_items
from idmtools.entities.simulation import Simulation
from idmtools.registry.functions import FunctionPluginManager

logger = getLogger(__name__)


@dataclass
class IPlatformSimulationOperations(CacheEnabled, ABC):
    """
    IPlatformSimulationOperations defines simulation item operations interface.
    """
    platform: 'IPlatform'  # noqa: F821
    platform_type: Type

    @abstractmethod
    def get(self, simulation_id: str, **kwargs) -> Any:
        """
        Returns the platform representation of an Simulation.

        Args:
            simulation_id: Item id of Simulations
            **kwargs:

        Returns:
            Platform Representation of an simulation
        """
        pass

    def pre_create(self, simulation: Simulation, **kwargs) -> NoReturn:
        """
        Run the platform/simulation post creation events.

        Args:
            simulation: simulation to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_pre_create_item")
        FunctionPluginManager.instance().hook.idmtools_platform_pre_create_item(item=simulation, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling pre_creation")
        simulation.pre_creation(self.platform)

    def post_create(self, simulation: Simulation, **kwargs) -> NoReturn:
        """
        Run the platform/simulation post creation events.

        Args:
            simulation: simulation to run post-creation events
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            NoReturn
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_create_item hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_create_item(item=simulation, kwargs=kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling post_creation")
        simulation.post_creation(self.platform)

    def create(self, simulation: Simulation, do_pre: bool = True, do_post: bool = True, **kwargs) -> Any:
        """
        Creates an simulation from an IDMTools simulation object.

        Also performs pre-creation and post-creation locally and on platform.

        Args:
            simulation: Simulation to create
            do_pre: Perform Pre creation events for item
            do_post: Perform Post creation events for item
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        if simulation.status is not None:
            return simulation
        if do_pre:
            self.pre_create(simulation, **kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Finished pre_create")
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling platform_create")
        simulation._platform_object = self.platform_create(simulation, **kwargs)
        if logger.isEnabledFor(DEBUG):
            logger.debug("Finished platform_create")
        if do_post:
            self.post_create(simulation, **kwargs)
            if logger.isEnabledFor(DEBUG):
                logger.debug("Finished post_create")
        return simulation

    @abstractmethod
    def platform_create(self, simulation: Simulation, **kwargs) -> Any:
        """
        Creates an simulation on Platform from an IDMTools Simulation Object.

        Args:
            simulation: Simulation to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the id of said item
        """
        pass

    def batch_create(self, sims: List[Simulation], display_progress: bool = True, **kwargs) -> List[Simulation]:
        """
        Provides a method to batch create simulations.

        Args:
            sims: List of simulations to create
            display_progress: Show progress bar
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        return batch_create_items(sims, create_func=self.create, display_progress=display_progress,
                                  progress_description="Commissioning Simulations", unit="simulation",
                                  **kwargs)

    @abstractmethod
    def get_parent(self, simulation: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error.

        Args:
            simulation:
            **kwargs:

        Returns:
            Parent of simulation

        Raise:
            TopLevelItem
        """
        pass

    def to_entity(self, simulation: Any, load_task: bool = False, parent: Optional[Experiment] = None,
                  **kwargs) -> Simulation:
        """
        Converts the platform representation of simulation to idmtools representation.

        Args:
            simulation:Platform simulation object
            load_task: Load Task Object as well. Can take much longer and have more data on platform
            parent: Optional parent object
        Returns:
            IDMTools simulation object
        """
        if parent:
            simulation.parent = parent
        return simulation

    def pre_run_item(self, simulation: Simulation, **kwargs):
        """
        Trigger right before commissioning experiment on platform.

        This ensures that the item is created. It also ensures that the children(simulations) have also been created.

        Args:
            simulation: Experiment to commission

        Returns:
            None
        """
        # ensure the item is created before running
        # TODO what status are valid here? Create only?
        if simulation.status is None:
            self.create(simulation, **kwargs)

    def post_run_item(self, simulation: Simulation, **kwargs):
        """
        Trigger right after commissioning experiment on platform.

        Args:
            simulation: Experiment just commissioned

        Returns:
            None
        """
        if logger.isEnabledFor(DEBUG):
            logger.debug("Calling idmtools_platform_post_run hooks")
        FunctionPluginManager.instance().hook.idmtools_platform_post_run(item=simulation, kwargs=kwargs)

    def run_item(self, simulation: Simulation, **kwargs):
        """
        Called during commissioning of an item. This should create the remote resource.

        Args:
            simulation:

        Returns:
            None
        """
        self.pre_run_item(simulation, **kwargs)
        self.platform_run_item(simulation, **kwargs)
        self.post_run_item(simulation, **kwargs)

    @abstractmethod
    def platform_run_item(self, simulation: Simulation, **kwargs):
        """
        Called during commissioning of an item. This should create the remote resource but not upload assets.

        Args:
            simulation: Simulation to run

        Returns:
            None
        """
        pass

    @abstractmethod
    def send_assets(self, simulation: Any, **kwargs):
        """
        Send simulations assets to server.

        Args:
            simulation: Simulation to upload assets for
            **kwargs: Keyword arguments for the op

        Returns:
            None
        """
        pass

    @abstractmethod
    def refresh_status(self, simulation: Simulation, **kwargs):
        """
        Refresh status for simulation object.

        Args:
            simulation: Experiment to get status for

        Returns:
            None
        """
        pass

    @abstractmethod
    def get_assets(self, simulation: Simulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Get files from simulation.

        Args:
            simulation: Simulation to fetch files from
            files: Files to get
            **kwargs:

        Returns:
            Dictionary containing filename and content
        """
        pass

    @abstractmethod
    def list_assets(self, simulation: Simulation, **kwargs) -> List[Asset]:
        """
        List available assets for a simulation.

        Args:
            simulation: Simulation of Assets

        Returns:
            List of filenames
        """
        pass

    def create_sim_directory_map(self, simulation_id: str) -> Dict:
        """
        Build simulation working directory mapping.
        Args:
            simulation_id: simulation id

        Returns:
            Dict
        """
        return {}

    def platform_delete(self, simulation_id: str) -> None:
        """
        Delete platform simulation.
        Args:
            simulation_id: simulation id
        Returns:
            None
        """
        pass

    def platform_cancel(self, simulation_id: str) -> None:
        """
        Cancel platform simulation.
        Args:
            simulation_id: simulation id
        Returns:
            None
        """
        pass
