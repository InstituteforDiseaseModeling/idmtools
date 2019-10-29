import os
import json
import collections
import typing
from dataclasses import dataclass, field
from idmtools.entities import IExperiment, CommandLine
from idmtools_model_emod.emod_simulation import EMODSimulation

if typing.TYPE_CHECKING:
    from idmtools_model_emod.defaults import iemod_default


@dataclass(repr=False)
class EMODExperiment(IExperiment):
    eradication_path: str = field(default=None, compare=False, metadata={"md": True})
    demographics: collections.OrderedDict = field(default_factory=lambda: collections.OrderedDict())
    legacy_exe: 'bool' = field(default=False, metadata={"md": True})

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=EMODSimulation)
        if self.eradication_path is not None:
            self.eradication_path = os.path.abspath(self.eradication_path)

    @classmethod
    def from_default(cls, name, default: 'iemod_default', eradication_path=None):
        base_simulation = EMODSimulation()
        default.process_simulation(base_simulation)

        exp = cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)
        exp.demographics.update(default.demographics())

        return exp

    @classmethod
    def from_files(cls, name, eradication_path=None, config_path=None, campaign_path=None, demographics_paths=None,
                   force=False):
        """
        Load custom |EMOD_s| files when creating :class:`EMODExperiment`.

        Args:
            name: The experiment name.
            eradication_path: The eradication.exe path.
            config_path: The custom configuration file.
            campaign_path: The custom campaign file.
            demographics_paths: The custom demographics files (single file or a list).
            force: True to always return, else throw an exception if something goes wrong.

        Returns:
            None
        """
        base_simulation = EMODSimulation()
        base_simulation.load_files(config_path, campaign_path, force)

        exp = cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)
        exp.add_demographics_file(demographics_paths, force)

        return exp

    def load_files(self, config_path=None, campaign_path=None, demographics_paths=None, force=False):
        """
        Load custom |EMOD_s| files from :class:`EMODExperiment`.

        Args:
            config_path: The custom configuration file.
            campaign_path: The custom campaign file.
            demographics_paths: The custom demographics files (single file or a list).
            force: True to always return, else throw an exception if something goes wrong.

        Returns:
            None
        """
        self.base_simulation.load_files(config_path, campaign_path, force)

        self.add_demographics_file(demographics_paths, force)

    def add_demographics_file(self, demographics_paths=None, force=False):
        """
        Load custom |EMOD_s| demographics files from :class:`EMODExperiment`.

        Args:
            demographics_paths: Path to custom demographics files (single file or a list).
            force: True to always return, else throw an exception if something goes wrong.

        Returns:
            None
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
        from idmtools.assets import Asset

        # Add Eradication.exe to assets
        self.assets.add_asset(Asset(absolute_path=self.eradication_path), fail_on_duplicate=False)

        # Clean up existing demographics files in case config got replaced
        config_demo_files = self.base_simulation.config.get("Demographics_Filenames", None)
        if config_demo_files:
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
        model_executable = os.path.basename(self.eradication_path)

        # Input path is different for legacy exes
        input_path = "./Assets;." if not self.legacy_exe else "./Assets"

        # We have everything we need for the command, create the object
        self.command = CommandLine(f"Assets/{model_executable}", "--config config.json", f"--input-path {input_path}")