import os
import typing
from dataclasses import dataclass, field
from idmtools.assets import Asset
from idmtools.core import experiment_factory
from idmtools.entities import IExperiment, CommandLine
from idmtools_models.dtk.DTKSimulation import DTKSimulation

if typing.TYPE_CHECKING:
    from idmtools_models.dtk.defaults import IDTKDefault


@dataclass(repr=False)
class DTKExperiment(IExperiment):
    eradication_path: str = field(default=None, compare=False, metadata={"md": True})

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=DTKSimulation)
        if self.eradication_path is not None:
            self.eradication_path = os.path.abspath(self.eradication_path)

    @classmethod
    def from_default(cls, name, default: 'IDTKDefault', eradication_path=None):
        base_simulation = DTKSimulation()
        default.process_simulation(base_simulation)
        return cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)

    @classmethod
    def from_files(cls, name, eradication_path=None, config_path=None, campaign_path=None, demographics_path=None,
                   force=False):
        """
        Provide a way to load custom files when creating DTKExperiment
        Args:
            name: experiment name
            eradication_path: eradication.exe path
            config_path: custom config file
            campaign_path: custom campaign file
            demographics_path: custom demographics file
            force: always return if True, else throw exception is something wrong
        Returns: None
        """
        base_simulation = DTKSimulation()
        base_simulation.load_files(config_path, campaign_path, demographics_path, force)

        return cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)

    def load_files(self, config_path=None, campaign_path=None, demographics_path=None, force=False):
        """
        Provide a way to load custom files from DTKExperiment
        Args:
            config_path: custom config file
            campaign_path: custom campaign file
            demographics_path: custom demographics file
            force: always return if True, else throw exception is something wrong
        Returns: None
        """
        self.base_simulation.load_files(config_path, campaign_path, demographics_path, force)

    def gather_assets(self) -> None:
        self.assets.add_asset(Asset(absolute_path=self.eradication_path))

    def pre_creation(self):
        super().pre_creation()

        # Create the command line according to the location of the model
        self.command = CommandLine("Assets/Eradication.exe", "--config config.json", "--input-path ./Assets;.")


experiment_factory.register_type(DTKExperiment)
