import json
import os
import typing
from dataclasses import dataclass, field

from idmtools.entities import IExperiment, CommandLine
from idmtools_model_emod.emod_file import DemographicsFiles
from idmtools_model_emod.emod_simulation import EMODSimulation

if typing.TYPE_CHECKING:
    from idmtools_model_emod.defaults import iemod_default


@dataclass(repr=False)
class EMODExperiment(IExperiment):
    eradication_path: str = field(default=None, compare=False, metadata={"md": True})
    legacy_exe: 'bool' = field(default=False, metadata={"md": True})
    demographics: 'DemographicsFiles' = field(default_factory=lambda: DemographicsFiles('demographics'))

    def __post_init__(self, simulation_type):
        super().__post_init__(simulation_type=EMODSimulation)
        if self.eradication_path is not None:
            self.eradication_path = os.path.abspath(self.eradication_path)

    @classmethod
    def from_default(cls, name, default: 'iemod_default', eradication_path=None):
        base_simulation = EMODSimulation()
        default.process_simulation(base_simulation)

        exp = cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)

        # Add the demographics
        for filename, content in default.demographics().items():
            exp.demographics.add_demographics_from_dict(content=content, filename=filename)

        return exp

    @classmethod
    def from_files(cls, name, eradication_path=None, config_path=None, campaign_path=None, demographics_paths=None):
        """
        Load custom |EMOD_s| files when creating :class:`EMODExperiment`.

        Args:
            name: The experiment name.
            eradication_path: The eradication.exe path.
            config_path: The custom configuration file.
            campaign_path: The custom campaign file.
            demographics_paths: The custom demographics files (single file or a list).

        Returns: An initialized experiment
        """

        def load_json_file(path):
            if not path:
                return
            try:
                with open(path, 'r') as fp:
                    return json.load(fp)
            except IOError as e:
                print(f"The file at {path} could not be loaded or parsed to JSON.\n{e}")

        base_simulation = EMODSimulation()
        base_simulation.config = load_json_file(config_path)["parameters"]
        base_simulation.campaign = load_json_file(campaign_path)

        # Create the experiment
        exp = cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)

        # Take care of the demographics files
        if isinstance(demographics_paths, str):
            demographics_paths = [demographics_paths]

        for demog_path in demographics_paths:
            exp.demographics.add_demographics_from_file(absolute_path=demog_path)

        return exp

    def gather_assets(self) -> None:
        from idmtools.assets import Asset

        # Add Eradication.exe to assets
        self.assets.add_asset(Asset(absolute_path=self.eradication_path), fail_on_duplicate=False)

        # Add demographics to assets
        self.assets.extend(self.demographics.gather_assets())

    def pre_creation(self):
        super().pre_creation()

        # Create the command line according to the location of the model
        model_executable = os.path.basename(self.eradication_path)

        # Input path is different for legacy exes
        input_path = "./Assets;." if not self.legacy_exe else "./Assets"

        # We have everything we need for the command, create the object
        self.command = CommandLine(f"Assets/{model_executable}", "--config config.json", f"--input-path {input_path}")

    def simulation(self):
        simulation = super().simulation()
        simulation.demographics.extend(self.demographics)
        return simulation
