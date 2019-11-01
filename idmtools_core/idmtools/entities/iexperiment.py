import copy
import os
import sys
import typing
import uuid
from abc import ABC
from itertools import chain
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, InitVar
from logging import getLogger
from more_itertools import grouper
from idmtools.core import ItemType, TExperimentBuilder
from idmtools.core.interfaces.entity_container import EntityContainer
from idmtools.core.interfaces.iassets_enabled import IAssetsEnabled
from idmtools.core.interfaces.inamed_entity import INamedEntity
from idmtools.entities.command_line import TCommandLine
from idmtools.entities.isimulation import TSimulationClass, TSimulation
from idmtools.utils.decorators import optional_yaspin_load
from idmtools import __version__


logger = getLogger(__name__)


@dataclass(repr=False)
class IExperiment(IAssetsEnabled, INamedEntity, ABC):
    """
    Class that represents a generic experiment.
    This class needs to be implemented for each model type with specifics.

    Args:
        name: The experiment name.
        simulation_type: A class to initialize the simulations that will be created for this experiment.
        assets: The asset collection for assets global to this experiment.
        base_simulation: Optional, a simulation that will be the base for all simulations created for this experiment.
        command: Command to run on simulations.
    """
    command: 'TCommandLine' = field(default=None)
    suite_id: uuid = field(default=None)
    simulation_type: 'InitVar[TSimulationClass]' = None
    base_simulation: 'TSimulation' = field(default=None, compare=False, metadata={"pickle_ignore": True})
    builders: set = field(default_factory=lambda: set(), compare=False, metadata={"pickle_ignore": True})
    simulations: EntityContainer = field(default_factory=lambda: EntityContainer(), compare=False,
                                         metadata={"pickle_ignore": True})
    _simulation_default: 'TSimulation' = field(default=None, compare=False)
    item_type: 'ItemType' = field(default=ItemType.EXPERIMENT, compare=False)

    def __post_init__(self, simulation_type):
        super().__post_init__()
        # Take care of the base simulation
        if not self.base_simulation:
            if simulation_type and callable(simulation_type):
                self.base_simulation = simulation_type()
            else:
                raise Exception(
                    "A `base_simulation` or `simulation_type` needs to be provided to the Experiment object!")

        self._simulation_default = self.base_simulation.__class__()

    def __repr__(self):
        return f"<Experiment: {self.uid} - {self.name} / Sim count {len(self.simulations) if self.simulations else 0}>"

    @property
    def builder(self) -> TExperimentBuilder:
        """
        For backward-compatibility purposes.

        Returns:
            The last ``TExperimentBuilder``.
        """
        return list(self.builders)[-1] if self.builders and len(self.builders) > 0 else None

    @builder.setter
    def builder(self, builder: TExperimentBuilder) -> None:
        """
        For backward-compatibility purposes.

        Args:
            builder: The new builder to be used.

        Returns:
            None
        """

        # Make sure we only take the last builder assignment
        if self.builders:
            self.builders.clear()

        self.add_builder(builder)

    def add_builder(self, builder: TExperimentBuilder) -> None:
        """
        Add builder to builder collection.

        Args:
            builder: A builder to be added.

        Returns:
            None
        """
        from idmtools.builders import ExperimentBuilder

        # Add builder validation
        if not isinstance(builder, ExperimentBuilder):
            raise Exception("Builder ({}) must have type of ExperimentBuilder!".format(builder))

        # Initialize builders the first time
        if self.builders is None:
            self.builders = set()

        # Add new builder to the collection
        self.builders.add(builder)

    def display(self):
        from idmtools.utils.display import display, experiment_table_display
        display(self, experiment_table_display)

    def batch_simulations(self, batch_size=5):
        # Make sure each simulation has platform and parent_id
        if self.simulations:
            for sim in self.simulations:
                sim.platform = self.platform
                sim.parent_id = self.uid

        # Consider simulations first
        for groups in grouper(self.simulations, batch_size):
            sims = []
            for sim in filter(None, groups):
                sims.append(sim)
            yield sims

        # Consider builders next
        if not self.builders:
            if not self.simulations:
                yield (self.simulation(),)
            return

        for groups in grouper(chain(*self.builders), batch_size):
            sims = []
            for simulation_functions in filter(None, groups):
                simulation = self.simulation()
                tags = {}

                for func in simulation_functions:
                    new_tags = func(simulation=simulation)
                    if new_tags:
                        tags.update(new_tags)

                simulation.tags = tags
                sims.append(simulation)

            yield sims

    def simulation(self):
        """
        Return a new simulation object.
        The simulation will be copied from the base simulation of the experiment.

        Returns:
            The created simulation.
        """
        sim = copy.deepcopy(self.base_simulation)
        sim.assets = copy.deepcopy(self.base_simulation.assets)
        sim.platform = self.platform
        sim.experiment = self
        return sim

    def pre_creation(self):
        # Gather the assets
        self.gather_assets()

        # Add a tag to keep the class name
        self.tags["type"] = f'{self.__class__.__module__}.{self.__class__.__name__}'

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
        return {"assets": AssetCollection(), "simulations": EntityContainer(), "builders": set(),
                "base_simulation": self._simulation_default}


@dataclass(repr=False)
class IWindowsExperiment:
    execution_platform = 'windows'


@dataclass(repr=False)
class ILinuxExperiment:
    execution_platform = 'linux'


@dataclass(repr=False)
class IGPUExperiment:
    is_gpu: bool = True


@dataclass(repr=False)
class IHostBinaryExperiment:
    pass


@dataclass(repr=False)
class IDockerExperiment:
    image_name: str
    # Optional config to build the docker image
    build: bool = False
    build_path: typing.Optional[str] = None
    # This should in the build_path directory
    Dockerfile: typing.Optional[str] = None
    pull_before_build: bool = True

    @optional_yaspin_load(text="Building docker image")
    def build_image(self, spinner=None, **extra_build_args):
        import docker
        from docker.errors import BuildError
        if spinner:
            spinner.text = f"Building {self.image_name}"
        # if the build_path is none use current working directory
        if self.build_path is None:
            self.build_path = os.getcwd()

        client = docker.client.from_env()
        build_config = dict(path=self.build_path, dockerfile=self.Dockerfile, tag=self.image_name,
                            labels=dict(
                                buildstamp=f'built-by idmtools {__version__}',
                                builddate=str(datetime.now(timezone(timedelta(hours=-8))))
                                )
                            )
        if extra_build_args:
            build_config.update(extra_build_args)
        logger.debug(f"Build configuration used: {str(build_config)}")

        try:
            result = client.images.build(**build_config)
            logger.info(f'Build Successful of {result[0].tag} ({result[0].id})')
        except BuildError as e:
            logger.info(f"Build failed for {self.image} with message {e.msg}")
            logger.info(f'Build log: {e.build_log}')
            sys.exit(-1)


@dataclass(repr=False)
class IDockerGPUExperiment(IGPUExperiment, IDockerExperiment):
    pass


TExperiment = typing.TypeVar("TExperiment", bound=IExperiment)
TGPUExperiment = typing.TypeVar("TGPUExperiment", bound=IGPUExperiment)
TDockerExperiment = typing.TypeVar("TDockerExperiment", bound=IDockerExperiment)
# class types
TExperimentClass = typing.Type[TExperiment]
TGPUExperimentClass = typing.Type[TGPUExperiment]
TDockerExperimentClass = typing.Type[TDockerExperiment]
# Composed types
TExperimentList = typing.List[typing.Union[TExperiment, str]]
TGPUExperimentList = typing.List[typing.Union[TGPUExperiment, str]]
TDockerExperimentList = typing.List[typing.Union[TDockerExperiment, str]]


class StandardExperiment(IExperiment):
    def __post_init__(self, simulation_type):
        from idmtools.entities.isimulation import StandardSimulation
        super().__post_init__(simulation_type=simulation_type or StandardSimulation)

    def gather_assets(self) -> None:
        pass
