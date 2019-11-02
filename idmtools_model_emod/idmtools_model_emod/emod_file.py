import json
import os
from abc import ABCMeta, abstractmethod

from idmtools.assets import Asset, AssetCollection, json_handler


class InputFilesList(AssetCollection, metaclass=ABCMeta):
    def __init__(self, relative_path=None):
        super().__init__()
        self.relative_path = relative_path

    @abstractmethod
    def set_simulation_config(self, simulation):
        pass

    def gather_assets(self):
        assets = [a for a in self.assets if not a.persisted]
        for a in assets:
            a.persisted = True
        return assets


class DemographicsFiles(InputFilesList):
    def set_simulation_config(self, simulation):
        simulation.config["Demographics_Filenames"] = [os.path.join(df.relative_path, df.filename) for df in self.assets]

    def add_demographics_from_file(self, absolute_path, filename: 'str' = None):
        filename = filename or os.path.basename(absolute_path)
        with open(absolute_path, 'r') as fp:
            asset = Asset(filename=filename, content=json.load(fp), relative_path=self.relative_path,
                          absolute_path=absolute_path, handler=json_handler)

        if asset in self.assets:
            raise Exception("Duplicated demographics file")

        self.assets.append(asset)

    def add_demographics_from_dict(self, content, filename):
        asset = Asset(filename=filename, content=content, relative_path=self.relative_path, handler=json_handler)
        if asset in self.assets:
            raise Exception("Duplicated demographics file")

        self.assets.append(asset)
