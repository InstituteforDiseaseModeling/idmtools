import typing

from idmtools.assets import Asset
from idmtools.entities import IExperiment, CommandLine
from idmtools_models.dtk.DTKSimulation import DTKSimulation

if typing.TYPE_CHECKING:
    from idmtools_models.dtk.defaults import IDTKDefault


class DTKExperiment(IExperiment):
    def __init__(self, name, assets=None, base_simulation=None, eradication_path=None):
        super().__init__(name=name, assets=assets, simulation_type=DTKSimulation, base_simulation=base_simulation)
        self.eradication_path = eradication_path

    @classmethod
    def from_default(cls, name, default: 'IDTKDefault', eradication_path=None):
        base_simulation = DTKSimulation()
        default().process_simulation(base_simulation)
        return cls(name=name, base_simulation=base_simulation, eradication_path=eradication_path)

    def gather_assets(self) -> None:
        self.assets.add_asset(Asset(absolute_path=self.eradication_path))

    def pre_creation(self):
        super().pre_creation()

        # Create the command line according to the location of the model
        self.command = CommandLine("Assets/Eradication.exe", "--config config.json", "--input-path ./Assets;.")
