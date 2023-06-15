import json
from dataclasses import dataclass, field
from typing import Type

from idmtools.assets import Asset, AssetCollection
from idmtools.entities import CommandLine
from idmtools.entities.itask import ITask
from idmtools.entities.simulation import Simulation
from idmtools.registry.task_specification import TaskSpecification


@dataclass(repr=False)
class TestTask(ITask):
    #command: CommandLine = field(default=CommandLine.from_string('echo this is a test'), metadata={"md": True})
    command: CommandLine = field(default=None, metadata={"md": True})
    parameters: dict = field(default_factory=lambda: {}, metadata={"md": True})
    common_asset_paths: list = field(default_factory=lambda: [])

    __test__ = False  # Hide from test discovery

    def set_parameter(self, name: str, value: any) -> dict:
        self.parameters[name] = value
        return {"name": value}

    def get_parameter(self, name, default=None):
        """
        Get a parameter in the simulation
        Args:
            name: Name of the parameter
        Returns:the Value of the parameter
        """
        return self.parameters.get(name, default)

    def update_parameters(self, params):
        """
        Bulk update parameters
        Args:
            params: dict with new values
        Returns:None
        """
        self.parameters.update(params)

    def gather_common_assets(self) -> AssetCollection:
        # modified for test (uid hashing means changing uids) copied version from python_task.py
        assets = [Asset(absolute_path=path) for path in self.common_asset_paths]
        return AssetCollection(assets=assets)

    def gather_transient_assets(self) -> AssetCollection:
        if not self.transient_assets.has_asset(filename="config.json"):
            self.transient_assets.add_asset(Asset(filename="config.json", content=json.dumps(self.parameters)))
        return self.transient_assets

    def reload_from_simulation(self, simulation: 'Simulation'):
        pass

    def __post_init__(self):
        if self.command is None:
            self.command = CommandLine.from_string('echo this is a test')


class TestTaskSpecification(TaskSpecification):

    def get(self, configuration: dict) -> TestTask:
        return TestTask(**configuration)

    def get_description(self) -> str:
        return "Defines a task that is just used for testing purposes"

    def get_type(self) -> Type[TestTask]:
        return TestTask
