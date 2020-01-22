import uuid
from dataclasses import dataclass, field
from logging import getLogger
from typing import NoReturn, Set
from idmtools.core import ItemType
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.platform_requirements import PlatformRequirements

logger = getLogger(__name__)


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
    simulations: EntityContainer = field(default_factory=lambda: EntityContainer(), compare=False,
                                         metadata={"pickle_ignore": True})
    item_type: ItemType = field(default=ItemType.EXPERIMENT, compare=False, init=False)
    task_type: str = field(default='idmtools.entities.command_task.CommandTask')
    platform_requirements: Set[PlatformRequirements] = field(default_factory=set)
    frozen: bool = field(default=False, init=False)

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
