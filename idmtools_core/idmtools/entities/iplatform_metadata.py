from abc import ABC, abstractmethod
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, List, Tuple, Type, Dict
from uuid import UUID
from idmtools.assets import AssetCollection
from idmtools.core import CacheEnabled
from idmtools.entities.iexperiment import IExperiment
from idmtools.entities.isimulation import ISimulation
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
        """
        Transfer Experiment assets to the platform.
        Args:
            experiment: Experiment to send assets for

        Returns:

        """
        pass

    @abstractmethod
    def refresh_status(self, experiment: IExperiment):
        """
        Refresh status for experiment object. This should update the object directly. For experiments it is best if
        all simulation states are updated as well

        Args:
            experiment: Experiment to get status for

        Returns:
            None
        """
        pass

    def get_assets(self, experiment: IExperiment, files: List[str], **kwargs) -> Dict[str, Dict[str, bytearray]]:
        """
        Get files from experiment

        Args:
            experiment: Experiment to get files from
            files: List files
            **kwargs:

        Returns:
            Dict with each sim id and the files contents matching specified list
        """
        ret = dict()
        for sim in experiment.simulations:
            ret[sim.uid] = self.platform._simulation.get_assets(sim, files, **kwargs)
        return ret

    def list_assets(self, experiment: IExperiment) -> Dict[str, List[str]]:
        """
        List assets available for experiment

        Args:
            experiment: Experiment to get assets for

        Returns:
            Dictionary of simulation and assets on each sim
        """
        ret = {}
        with ThreadPoolExecutor() as pool:
            futures = dict()
            for sim in experiment.simulations:
                future = pool.submit(self.platform._simulations.list_assets, sim)
                futures[future] = sim

            for future in as_completed(futures):
                ret[futures[future]] = future.result()
        return ret


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
        """
        Refresh status of suite
        Args:
            experiment:

        Returns:

        """
        pass

    def get_assets(self, suite: Suite, files: List[str], **kwargs) -> Dict[str, Dict[str, Dict[str, bytearray]]]:
        """
        Fetch assets for suite
        Args:
            suite: suite to get assets for
            files: Files to load
            **kwargs:

        Returns:
            Nested dictionaries in the structure
            experiment_id { simulation_id { files = content } } }
        """
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
        """
        Refresh status for workflow item
        Args:
            workflow_item: Item to refresh status for

        Returns:
            None
        """
        pass

    @abstractmethod
    def send_assets(self, workflow_item: Any):
        """
        Send assets for workflow item to platform

        Args:
            workflow_item: Item to send assets for

        Returns:

        """
        pass

    @abstractmethod
    def get_assets(self, workflow_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Load assets for workflow item
        Args:
            workflow_item: Item
            files: List of files to load
            **kwargs:

        Returns:
            Dictionary with filename as key and value as binary content
        """
        pass

    @abstractmethod
    def list_assets(self, workflow_item: IWorkflowItem) -> List[str]:
        """
        List files available  for workflow item

        Args:
            workflow_item: Workflow item

        Returns:
            List of filenames
        """
        pass


@dataclass
class IPlatformAssetCollectionOperations(CacheEnabled, ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def create(self, asset_collection: AssetCollection, **kwargs) -> Tuple[Any, UUID]:
        """
        Creates an workflow_item from an IDMTools AssetCollection object

        Args:
            asset_collection: AssetCollection to create
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Created platform item and the UUID of said item
        """
        pass

    def batch_create(self, asset_collections: List[AssetCollection], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create asset collections items

        Args:
            asset_collections: List of asset collection items to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for ac in asset_collections:
            ret.append(self.create(ac, **kwargs))
        return ret

    @abstractmethod
    def get(self, asset_collection_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an AssetCollection

        Args:
            asset_collection_id: Item id of AssetCollection
            **kwargs:

        Returns:
            Platform Representation of an AssetCollection
        """
        pass

    def to_entity(self, asset_collection: Any, **kwargs) -> AssetCollection:
        """
        Converts the platform representation of AssetCollection to idmtools representation

        Args:
            asset_collection: Platform AssetCollection object

        Returns:
            IDMTools suite object
        """
        return asset_collection



@dataclass
class IPlatformWorkItemOperations(CacheEnabled, ABC):
    platform: 'IPlatform'
    platform_type: Type

    @abstractmethod
    def get(self, work_item_id: UUID, **kwargs) -> Any:
        """
        Returns the platform representation of an WorkflowItem

        Args:
            workflow_item_id: Item id of WorkflowItems
            **kwargs:

        Returns:
            Platform Representation of an work_item
        """
        pass

    def batch_create(self, work_items: List[IWorkflowItem], **kwargs) -> List[Tuple[Any, UUID]]:
        """
        Provides a method to batch create workflow items

        Args:
            workflow_items: List of work items to create
            **kwargs:

        Returns:
            List of tuples containing the create object and id of item that was created
        """
        ret = []
        for wi in work_items:
            ret.append(self.create(wi, **kwargs))
        return ret

    @abstractmethod
    def create(self, workf_item: IWorkflowItem, **kwargs) -> Tuple[Any, UUID]:
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
    def get_parent(self, work_item: Any, **kwargs) -> Any:
        """
        Returns the parent of item. If the platform doesn't support parents, you should throw a TopLevelItem error

        Args:
            work_item:
            **kwargs:

        Returns:

        Raise:
            TopLevelItem
        """
        pass

    @abstractmethod
    def get_children(self, work_item: Any, **kwargs) -> List[Any]:
        """
        Returns the children of an workflow_item object

        Args:
            work_item: WorkflowItem object
            **kwargs: Optional arguments mainly for extensibility

        Returns:
            Children of work_item object
        """
        pass

    def to_entity(self, work_item: Any, **kwargs) -> IWorkflowItem:
        """
        Converts the platform representation of workflow_item to idmtools representation

        Args:
            work_item:Platform workflow_item object

        Returns:
            IDMTools workflow_item object
        """
        return work_item

    @abstractmethod
    def refresh_status(self, work_item: IWorkflowItem):
        """
        Refresh status for workflow item
        Args:
            work_item: Item to refresh status for

        Returns:
            None
        """
        pass

    @abstractmethod
    def send_assets(self, work_item: Any):
        """
        Send assets for workflow item to platform

        Args:
            work_item: Item to send assets for

        Returns:

        """
        pass

    @abstractmethod
    def get_assets(self, work_item: IWorkflowItem, files: List[str], **kwargs) -> Dict[str, bytearray]:
        """
        Load assets for workflow item
        Args:
            workflow_item: Item
            files: List of files to load
            **kwargs:

        Returns:
            Dictionary with filename as key and value as binary content
        """
        pass

    @abstractmethod
    def list_assets(self, work_item: IWorkflowItem) -> List[str]:
        """
        List files available  for workflow item

        Args:
            work_item: Workflow item

        Returns:
            List of filenames
        """
        pass