import uuid
from dataclasses import dataclass, field, InitVar
from logging import getLogger
from types import GeneratorType
from typing import NoReturn, Set, Union, Iterator

from idmtools.core import ItemType
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.platform_requirements import PlatformRequirements
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools.utils.collections import ParentIterator

logger = getLogger(__name__)

SUPPORTED_SIM_TYPE = Union[EntityContainer, GeneratorType, TemplatedSimulations, Iterator]


@dataclass(repr=False)
class Experiment(IAssetsEnabled, INamedEntity):
    """
    Class that represents a generic experiment.
    This class needs to be implemented for each model type with specifics.

    Args:
        name: The experiment name.
        assets: The asset collection for assets global to this experiment.
    """
    suite_id: uuid = field(default=None)

    item_type: ItemType = field(default=ItemType.EXPERIMENT, compare=False, init=False)
    task_type: str = field(default='idmtools.entities.command_task.CommandTask')
    platform_requirements: Set[PlatformRequirements] = field(default_factory=set)
    frozen: bool = field(default=False, init=False)
    simulations: InitVar[SUPPORTED_SIM_TYPE] = None
    __simulations: Union[SUPPORTED_SIM_TYPE] = field(default_factory=lambda: EntityContainer(), compare=False)

    def __post_init__(self, simulations):
        super().__post_init__()
        if simulations is not None and not isinstance(simulations, property):
            self.simulations = simulations
        self.__simulations.parent = self

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations) if self.simulations else 0}>"

    @property
    def suite(self):
        return self.parent

    @suite.setter
    def suite(self, suite):
        self.parent = suite

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def pre_creation(self) -> None:
        # Gather the assets
        self.gather_assets()

        # TODO How to handle genreators?
        if "task_type" not in self.tags and not isinstance(self.simulations, GeneratorType) and \
                (not isinstance(self.simulations, ParentIterator) or
                 (isinstance(self.simulations, ParentIterator)
                  and not isinstance(self.simulations.items, TemplatedSimulations)
                 )):
            task_class = self.simulations[0].task.__class__
            self.tags["task_type"] = f'{task_class.__module__}.{task_class.__name__}'
        # to keep experiments clean, let's only do this is we have a special experiment class
        if self.__class__ is not Experiment:
            # Add a tag to keep the Experiment class name
            self.tags["experiment_type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

    @property
    def done(self):
        return all([s.done for s in self.simulations])

    @property
    def succeeded(self):
        return all([s.succeeded for s in self.simulations])

    @property
    def simulations(self):
        return ParentIterator(self.__simulations, parent=self)

    @simulations.setter
    def simulations(self, simulations: Union[SUPPORTED_SIM_TYPE]):
        if isinstance(simulations, (GeneratorType, TemplatedSimulations, EntityContainer)):
            self.__simulations = simulations
        elif isinstance(simulations, (list, set)):
            self.simulations = EntityContainer(simulations)
        else:
            raise ValueError("You can only set simulations to an EntityContainer, a Generator, a TemplatedSimulations "
                             "or a List/Set of Simulations")

    @property
    def simulation_count(self):
        return len(self.simulations)

    def refresh_simulations(self):
        from idmtools.core import ItemType
        self.simulations = self.platform.get_children(self.uid, ItemType.EXPERIMENT, force=True)

    def refresh_simulations_status(self):
        self.platform.refresh_status(item=self)

    def pre_getstate(self):
        """
        Return default values for :meth:`~idmtools.interfaces.ientity.pickle_ignore_fields`.
        Call before pickling.
        """
        from idmtools.assets import AssetCollection
        return {"assets": AssetCollection(), "simulations": EntityContainer()}

    def gather_assets(self) -> NoReturn:
        # TODO assets gathering magic.... easy if we pre-populate our sims.. hard in generators
        # we could let it be more user facing or wrapped by convenience functions per model
        pass
