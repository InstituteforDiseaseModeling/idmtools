import ast
import typing
import uuid
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, fields
from logging import getLogger

from idmtools.core.interfaces.ientity import IEntity

if typing.TYPE_CHECKING:
    from idmtools.entities.iexperiment import TExperiment
    from idmtools.entities.isimulation import TSimulationBatch, TSimulation
    from typing import List, Any
    from idmtools.core import ObjectType

logger = getLogger(__name__)

CALLER_LIST = ['_create_from_block',  # create platform through Platform Factory
               'fetch',  # create platform through un-pickle
               'get'  # create platform through platform spec' get method
               ]


@dataclass(repr=False)
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
        """
        Trace the stack and find the caller
        Returns: the direct caller
        """
        import inspect

        s = inspect.stack()
        return s[2][3]

    def __new__(cls, *args, **kwargs):
        """
        Here is the code to create a new object!
        Args:
            args: user inputs
            kwargs: user inputs
        Returns: object created
        """

        # Check the caller
        caller = cls.get_caller()

        # Action based on the caller
        if caller in CALLER_LIST:
            return super().__new__(cls)
        else:
            raise ValueError(
                f"Please use Factory to create Platform! For example: \n    platform = Platform('COMPS', **kwargs)")

    def __post_init__(self) -> None:
        """
        Work to be done after object creation
        Returns: None
        """
        self.validate_inputs_types()

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

    def __repr__(self):
        return f"<Platform {self.__class__.__name__} - id: {self.uid}>"

    def validate_inputs_types(self) -> None:
        """
        Validate user inputs and case attr with the correct data types
        Returns: None
        """
        # retrieve field values, default values and types
        fds = fields(self)
        field_value = {f.name: getattr(self, f.name) for f in fds}
        field_type = {f.name: f.type for f in fds}

        # Make sure the user values have the requested type
        fs_kwargs = set(field_type.keys()).intersection(set(field_value.keys()))
        for fn in fs_kwargs:
            ft = field_type[fn]
            if ft in (int, float, str):
                field_value[fn] = ft(field_value[fn]) if field_value[fn] is not None else field_value[fn]
            elif ft is bool:
                field_value[fn] = ast.literal_eval(field_value[fn]) if isinstance(field_value[fn], str) else \
                    field_value[fn]

        # Update attr with validated data types
        for fn in fs_kwargs:
            setattr(self, fn, field_value[fn])

    @abstractmethod
    def get_object(self, object_id: 'uuid', force: 'bool' = False, raw: 'bool' = False, object_type: 'ObjectType' = None, **kwargs) -> any:
        """
        Get an object from the platform.
        This object can get anything from Experiment, Suite, Simulations.

        The object can either be returned raw (meaning in the platform format) or as an idmtools entity.

        If no `object_type` is provided, the function will sequentially ask the platform for all available object type.
        If no object is found, an exception is raised.

        This function is memoizing the return value in order to save time when the same object is retrieved.
        The `force` parameter allows to force bypassing the cache and fetching a fresh object from the platform.
        The objects cached have a 60 seconds timeout.

        Args:
            object_id: ID of the object on the platform
            force: bypass the cache if True
            raw: if True, returns a platform object, else returns an idmtools entity
            object_type: Specify the type of object for faster retrieval
            **kwargs:

        Returns: idmtools/platform object with the given id
        Raises: RuntimeError if not found

        """
        pass

    @abstractmethod
    def get_parent(self, object_id: 'uuid', force: 'bool' = False, object_type: 'ObjectType' = None,
                   raw: 'bool' = False):
        """
        Get the parent of the object identified by `object_id`.
        Similarly to `IPlatform.get_object`, this function accepts `force`, `object_type` and `raw`.

        Args:
            object_id: ID of the object we want the parent
            force: Bypass the cache if True
            object_type: Type of the object identified by `object_id` for faster retrieval
            raw: if True platform object, else idmtools entity

        Returns: parent if exists, None if not
        Raises: RuntimeError if `object_id` does not exist on the platform
        """
        pass

    @abstractmethod
    def get_children(self, object_id: 'uuid', force: 'bool' = False, object_type: 'ObjectType' = None,
                     raw: 'bool' = False) -> 'any':
        """
        Get the children of the object identified by `object_id`.
        Similarly to `IPlatform.get_object`, this function accepts `force`, `object_type` and `raw`.

        Args:
            object_id: ID of the object we want children from
            force: Bypass the cache if True
            object_type: Type of the object identified by `object_id` for faster retrieval
            raw: if True platform object, else idmtools entity

        Returns: children if exists, None if not
        Raises: RuntimeError if `object_id` does not exist on the platform

        """
        pass


TPlatform = typing.TypeVar("TPlatform", bound=IPlatform)
TPlatformClass = typing.Type[TPlatform]
