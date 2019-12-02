from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List, Tuple, Type, Dict
from uuid import UUID

from idmtools.core import CacheEnabled
from idmtools.entities.iexperiment import IExperiment
from idmtools.entities.isimulation import  ISimulation
from idmtools.entities.suite import Suite
from idmtools.entities.iworkflow_item import IWorkflowItem


@dataclass
class IPlatformExperimentOperations(ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, experiment_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an Experiment

        Args:
            experiment_id: Item id of Experiments
            **kwargs:

        Returns:
            Platform Representation of an experiment
        """
        pass

    @abstractmethod
    def create(self, experiment: IExperiment, **kwargs) -> Tuple[IExperiment, UUID]:
        """
        Creates an experiment from an IDMTools experiment object

        Args:
            experiment: Experiment to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    def batch_create(self, experiments: List[IExperiment], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create experiments

        Args:
            experiments: List of experiments to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for exp in experiments:
            ret.append(self.create(exp, **kwargs))
        return ret

    @abstractmethod
    def get_children(self, experiment: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an experiment object

        Args:
            experiment: Experiment object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of experiment object
        """
        pass

    @abstractmethod
    def get_parent(self, experiment: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error
        
        Args:
            experiment:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    def to_entity(self, experiment: Any, **kwargs) -> IExperiment:
        """
        Converts the platform representation of experiment to idmtools representation
        
        Args:
            experiment:Platform experiment object 

        Returns:
            IDMTools experiment object
        """
        return experiment

    @abstractmethod
    def run_item(self, experiment: IExperiment):
        """
        Called during commissioning of an item. This should create the remote resource
        
        Args:
            experiment: 

        Returns:

        """
        pass
    
    @abstractmethod
    def send_assets(self, experiment: Any):
        pass

    @abstractmethod
    def refresh_status(self, experiment: IExperiment):
        pass

    def get_assets(self, experiment: IExperiment, files: List[str], **kwargs) -> Dict[str, Dict[str, bytearray]]:
        ret = dict()
        for sim in experiment.simulations:
            ret[sim.uid] = self.platform._simulation.get_assets(sim, files, **kwargs)
        return ret

    @abstractmethod
    def list_assets(self, experiment: IExperiment) -> List[str]:
        pass


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

    @abstractmethod
    def create(self, simulation: ISimulation, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an simulation from an IDMTools simulation object

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
        pass

    @abstractmethod
    def get_assets(self, simulation: ISimulation, files: List[str], **kwargs) -> Dict[str, bytearray]:
        pass

    @abstractmethod
    def list_assets(self, simulation: ISimulation) -> List[str]:
        pass


@dataclass
class IPlatformSuiteOperations(ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, suite_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an Suite

        Args:
            suite_id: Item id of Suites
            **kwargs:

        Returns:
            Platform Representation of an suite
        """
        pass

    def batch_create(self, suites: List[Suite], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create suites

        Args:
            suites: List of suites to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for suite in suites:
            ret.append(self.create(suite, **kwargs))
        return ret

    @abstractmethod
    def create(self, suite: Suite, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an suite from an IDMTools suite object

        Args:
            suite: Suite to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    @abstractmethod
    def get_parent(self, suite: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            suite:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    @abstractmethod
    def get_children(self, suite: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an suite object

        Args:
            suite: Suite object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of suite object
        """
        pass

    def to_entity(self, suite: Any, **kwargs) -> Suite:
        """
        Converts the platform representation of suite to idmtools representation

        Args:
            suite:Platform suite object 

        Returns:
            IDMTools suite object
        """
        return suite

    @abstractmethod
    def refresh_status(self, experiment: Suite):
        pass

    def get_assets(self, suite: Suite, files: List[str], **kwargs) -> Dict[str, Dict[str, Dict[str, bytearray]]]:
        ret = dict()
        for exp in suite.experiments:
            ret[exp.uid] = self.platform._experiments.get_assets(exp, files, **kwargs)
        return ret


@dataclass
class IPlatformWorkflowItemOperations(CacheEnabled, ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, workflow_item_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an WorkflowItem

        Args:
            workflow_item_id: Item id of WorkflowItems
            **kwargs:

        Returns:
            Platform Representation of an workflow_item
        """
        pass

    def batch_create(self, workflow_items: List[IWorkflowItem], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create workflow items

        Args:
            workflow_items: List of worfklow items to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for wi in workflow_items:
            ret.append(self.create(wi, **kwargs))
        return ret

    @abstractmethod
    def create(self, workflow_item: IWorkflowItem, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an workflow_item from an IDMTools workflow_item object

        Args:
            workflow_item: WorkflowItem to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    @abstractmethod
    def get_parent(self, workflow_item: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            workflow_item:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    @abstractmethod
    def get_children(self, workflow_item: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an workflow_item object

        Args:
            workflow_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of workflow_item object
        """
        pass

    def to_entity(self, workflow_item: Any, **kwargs) -> IWorkflowItem:
        """
        Converts the platform representation of workflow_item to idmtools representation

        Args:
            workflow_item:Platform workflow_item object 

        Returns:
            IDMTools workflow_item object
        """
        return workflow_item

    @abstractmethod
    def refresh_status(self, workflow_item: IWorkflowItem):
        pass

    @abstractmethod
    def send_assets(self, workflow_item: Any):
        pass

    @abstractmethod
    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        pass

    @abstractmethod
    def list_assets(self, workflow_item: IWorkflowItem) -> List[str]:
        pass


@dataclass
class IPlatformAssetCollectionOperations(CacheEnabled, ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, asset_collection_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an AssetCollection

        Args:
            asset_collection_id: Item id of WorkflowItems
            **kwargs:

        Returns:
            Platform Representation of an workflow_item
        """
        pass