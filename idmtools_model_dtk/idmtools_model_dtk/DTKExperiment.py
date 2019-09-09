import os
import json
import collections
import typing
from dataclasses import dataclass, field
from idmtools.assets import Asset
from idmtools.entities import IExperiment, CommandLine
from idmtools_model_dtk.DTKSimulation import DTKSimulation
# from idmtools_model_dtk.idmtools_model_dtk.DTKSimulation import DTKSimulation

if typing.TYPE_CHECKING:
    # from idmtools_model_dtk.defaults import IDTKDefault
    from idmtools_model_dtk.idmtools_model_dtk.defaults.IDTKDefault import IDTKDefault


@dataclass(repr=False)
class DTKExperiment(IExperiment):
    eradication_path: str = field(default=None, compare=False, metadata={"md": True})
    demographics: collections.OrderedDict = field(default_factory=lambda: collections.OrderedDict())

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=DTKSimulation)
        if self.eradication_path:
            self.eradication_path = os.path.abspath(self.eradication_path)

    @classmethod
    def from_default(cls, name, default: 'IDTKDefault', eradication_path=None):
        base_simulation = DTKSimulation()
        default.process_simulation(base_simulation)

        exp = cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)
        exp.demographics.update(default.demographics())

        return exp

    @classmethod
    def from_files(cls, name, eradication_path=None, config_path=None, campaign_path=None, demographics_paths=None,
                   force=False):
        """
        Provide a way to load custom files when creating DTKExperiment
        Args:
            name: experiment name
            eradication_path: eradication.exe path
            config_path: custom config file
            campaign_path: custom campaign file
            demographics_paths: custom demographics files (single file or a list)
            force: always return if True, else throw exception if something wrong
        Returns: None
        """
        base_simulation = DTKSimulation()
        base_simulation.load_files(config_path, campaign_path, force)

        exp = cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)
        exp.add_demographics_file(demographics_paths, force)

        return exp

    def load_files(self, config_path=None, campaign_path=None, demographics_paths=None, force=False):
        """
        Provide a way to load custom files from DTKExperiment
        Args:
            config_path: custom config file
            campaign_path: custom campaign file
            demographics_paths: custom demographics files (single file or a list)
            force: always return if True, else throw exception if something wrong
        Returns: None
        """
        self.base_simulation.load_files(config_path, campaign_path, force)

        self.add_demographics_file(demographics_paths, force)

    def add_demographics_file(self, demographics_paths=None, force=False):
        """
        Provide a way to load custom files
        Args:
            demographics_paths: custom demographics files (single file or a list)
            force: always return if True, else throw exception is something wrong
        Returns: None
        """

        def load_file(file_path):
            try:
                with open(file_path, 'rb') as f:
                    return json.load(f)
            except IOError:
                if not force:
                    raise Exception(f"Encounter issue when loading file: {file_path}")
                else:
                    return None

        if demographics_paths:
            if isinstance(demographics_paths, collections.Iterable) \
                    and not isinstance(demographics_paths, str):
                demographics_paths = demographics_paths
            else:
                demographics_paths = [demographics_paths]

            for demographics_path in demographics_paths:
                jn = load_file(demographics_path)
                if jn:
                    self.demographics.update({os.path.basename(demographics_path): jn})
                    self.base_simulation.update_config_demographics_filenames(os.path.basename(demographics_path))

    def gather_assets(self) -> None:
        # Add Eradication.exe to assets
        self.assets.add_asset(Asset(absolute_path=self.eradication_path))

        # Clean up existing demographics files in case config got replaced
        config_demo_files = self.base_simulation.config["Demographics_Filenames"]
        exp_demo_files = list(self.demographics.keys())
        for f in exp_demo_files:
            if f not in config_demo_files:
                self.demographics.pop(f)

        # Add demographics to assets
        for filename, content in self.demographics.items():
            self.assets.add_asset(Asset(filename=filename, content=json.dumps(content)), fail_on_duplicate=False)

    def pre_creation(self):
        super().pre_creation()

        # Create the command line according to the location of the model
        self.command = CommandLine("Assets/Eradication.exe", "--config config.json", "--input-path ./Assets;.")
