import copy
import hashlib
import os
import collections
import stat
import typing
from abc import ABC
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from urllib.parse import urlparse
import requests
from idmtools.entities.command_line import CommandLine
from idmtools.entities.experiment import IDockerModel
from idmtools.entities.imodel import IModel
from idmtools.utils.decorators import optional_yaspin_load
from idmtools_model_emod.emod_file import DemographicsFiles, MigrationFiles, Dlls

if typing.TYPE_CHECKING:
    from idmtools_model_emod import IEMODDefault

logger = getLogger(__name__)


@dataclass(repr=False)
class IEMODModel(IModel, ABC):
    eradication_path: str = field(default=None, compare=False, metadata={"md": True})
    demographics: collections.OrderedDict = field(default_factory=lambda: collections.OrderedDict())
    legacy_exe: 'bool' = field(default=False, metadata={"md": True})
    demographics: 'DemographicsFiles' = field(default_factory=lambda: DemographicsFiles('demographics'))
    dlls: 'Dlls' = field(default_factory=lambda: Dlls())
    migrations: 'MigrationFiles' = field(default_factory=lambda: MigrationFiles('migrations'))

    def __post_init__(self):
        super().__post_init__()
        self.executable_name = "Eradication.exe"
        if self.eradication_path is not None:
            self.executable_name = os.path.basename(self.eradication_path)
            if urlparse(self.eradication_path).scheme in ('http', 'https',):
                self.eradication_path = self.download_eradication(self.eradication_path)
            self.eradication_path = os.path.abspath(self.eradication_path)

    @staticmethod
    @optional_yaspin_load(text='Downloading file')
    def download_eradication(url, spinner=None):
        # download eradication from path to our local_data cache
        cache_path = os.path.join(str(Path.home()), '.local_data', "eradication-cache")
        filename = hashlib.md5(url.encode('utf-8')).hexdigest()
        out_name = os.path.join(cache_path, filename)
        os.makedirs(cache_path, exist_ok=True)
        if not os.path.exists(out_name):
            if spinner:
                spinner.text = f"Downloading {url} to {out_name}"
            logger.debug(f"Downloading {url} to {out_name}")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(out_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
            # ensure on linux we make it executable locally
            if os.name != 'nt':
                st = os.stat(out_name)
                os.chmod(out_name, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.debug(f"Finished downloading {url}")
        else:
            logger.debug(f'{url} already cached as {out_name}')
        return out_name

    @classmethod
    def from_default(cls, name, default: 'IEMODDefault', eradication_path=None):
        exp = cls(name=name, eradication_path=eradication_path)

        # Set the base simulation
        default.process_simulation(exp.base_simulation)

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
        # Create the experiment
        exp = cls(name=name, eradication_path=eradication_path)

        # Load the files
        exp.base_simulation.load_files(config_path=config_path, campaign_path=campaign_path)

        if demographics_paths:
            for demog_path in [demographics_paths] if isinstance(demographics_paths, str) else demographics_paths:
                exp.demographics.add_demographics_from_file(demog_path)

        return exp

    def gather_assets(self) -> typing.NoReturn:
        from idmtools.assets import Asset

        # Add Eradication.exe to assets
        logger.debug(f"Adding {self.eradication_path}")
        self.assets.add_asset(Asset(absolute_path=self.eradication_path, filename=self.executable_name),
                              fail_on_duplicate=False)

        # Add demographics to assets
        self.assets.extend(self.demographics.gather_assets())

        # Add DLLS to assets
        self.assets.extend(self.dlls.gather_assets())

        # Add the migrations
        self.assets.extend(self.migrations.gather_assets())

    def pre_creation(self):
        super().pre_creation()

        # Input path is different for legacy exes
        input_path = r"./Assets\;." if not self.legacy_exe else "./Assets"

        # Create the command line according to self. location of the model
        self.command = CommandLine(f"Assets/{self.executable_name}", "--config config.json",
                                   f"--input-path {input_path}", f"--dll-path ./Assets")

    def simulation(self):
        simulation = super().simulation()
        # Copy the experiment demographics and set them as persisted to prevent change
        # TODO: change persisted to the frozen mechanism when done
        demog_copy = copy.deepcopy(self.demographics)
        demog_copy.set_all_persisted()
        # Add them to the simulation
        simulation.demographics.extend(demog_copy)

        # Tale care of the migrations
        migration_copy = copy.deepcopy(self.migrations)
        migration_copy.set_all_persisted()
        simulation.migrations.merge_with(migration_copy)

        # Handle the custom reporters
        self.dlls.set_simulation_config(simulation)

        return simulation


@dataclass(repr=False)
class EMODModel(IEMODModel):
    pass


@dataclass(repr=False)
class DockerEMODModel(IEMODModel, IDockerModel):
    image_name: str = 'idm-docker-public.packages.idmod.org/idm/centos:dtk-runtime'

    def __post_init__(self):
        super().__post_init__()
        if os.name != "nt" and self.eradication_path is not None and self.eradication_path.endswith(".exe"):
            raise ValueError("You are attempting to use a Windows Eradication executable on a linux experiment")

    @classmethod
    def from_default(cls, name, default: 'IEMODDefault',
                     image_name: str = 'idm-docker-public.packages.idmod.org/idm/centos:dtk-runtime',
                     eradication_path=None):
        exp = cls(name=name, eradication_path=eradication_path, image_name=image_name)

        # Set the base simulation
        default.process_simulation(exp.base_simulation)

        # Add the demographics
        for filename, content in default.demographics().items():
            exp.demographics.add_demographics_from_dict(content=content, filename=filename)

        return exp
