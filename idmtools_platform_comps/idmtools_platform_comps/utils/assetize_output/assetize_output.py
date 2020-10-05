import re

import tempfile
import inspect
import os
from dataclasses import dataclass, field
from logging import getLogger
from COMPS.Data.CommissionableEntity import CommissionableEntity
from functools import partial
from typing import List, Union, Callable, Dict
from idmtools.core import EntityStatus
from idmtools.core.interfaces.irunnable_entity import IRunnableEntity
from idmtools.entities.experiment import Experiment
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iworkflow_item import IWorkflowItem
from idmtools.entities.simulation import Simulation
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


EntityFilterFunc = Callable[[CommissionableEntity], bool]
AssetizableItem = Union[Experiment, Simulation, IWorkflowItem]
logger = getLogger(__name__)
user_logger = getLogger("user")


@dataclass(repr=False)
class AssetizeOutput(SSMTWorkItem):
    file_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=lambda: ["StdErr.txt", "StdOut.txt", "WorkOrder.json", "*.log"])
    include_assets: bool = field(default=False)
    simulation_prefix_format_str: str = field(default="{simulation.id}")
    no_simulation_prefix: bool = field(default=False)
    verbose: bool = field(default=False)
    work_item_prefix_format_str: str = field(default=None)
    pre_run_functions: List[Callable] = field(default_factory=list)
    entity_filter_function: EntityFilterFunc = field(default=None)
    asset_tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.item_name = "Assetize Output"

    def create_command(self) -> str:
        command = "python3 Assets/assetize_ssmt_script.py "
        for pattern in self.file_patterns:
            command += f'--file-pattern "{pattern}"'

        for pattern in self.exclude_patterns:
            command += f' --exclude-pattern "{pattern}"'

        for name, value in self.asset_tags.items():
            command += f' --asset-tag "{name}={value}"'

        if self.no_simulation_prefix:
            command += f' --no-simulation-prefix'
        else:
            command += f' --simulation-prefix-format-str "{self.simulation_prefix_format_str}"'

        if self.work_item_prefix_format_str:
            command += f' --work_item_prefix_format_str "{self.work_item_prefix_format_str}"'

        if self.include_assets:
            command += f' --assets'

        for pre_run_func in self.pre_run_functions:
            command += f' --pre-run-func {pre_run_func.__name__}'

        if self.entity_filter_function:
            command += f' --entity-filter-func {self.entity_filter_function.__name__}'

        if self.verbose:
            command += f' --verbose'

        return command

    def __pickle_pre_run(self):
        if self.pre_run_functions:
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "pre_run.py")
            file = open(temp_file, 'w')
            for function in self.pre_run_functions:
                new_source = self.__format_function_source(function)
                file.write("\n".join(new_source))
            file.close()
            self.asset_files.add_file(temp_file)

    def __pickle_filter_func(self):
        if self.entity_filter_function:
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "entity_filter_func.py")
            file = open(temp_file, 'w')
            new_source = self.__format_function_source(self.entity_filter_function)
            file.write("\n".join(new_source))
            file.close()
            self.asset_files.add_file(temp_file)

    @staticmethod
    def __format_function_source(function):
        source = inspect.getsource(function).splitlines()
        space_base = 0
        while source[0][space_base] == " ":
            space_base += 1
        replace_expr = re.compile("^[ ]{" + str(space_base) + "}")
        new_source = []
        for line in source:
            new_source.append(replace_expr.sub("", line))
        return new_source

    def clear_exclude_patterns(self):
        self.exclude_patterns = []

    def pre_creation(self, platform: IPlatform) -> None:
        super().pre_creation(platform)
        self.__ensure_all_dependencies_created(platform)
        if len(self.asset_tags) == 0:
            for experiment in self.related_experiments:
                self.asset_tags['AssetizedOutputfromFromExperiment'] = str(experiment.id)
            for simulation in self.related_simulations:
                self.asset_tags['AssetizedOutputfromFromSimulation'] = str(simulation.id)
            for work_item in self.related_work_items:
                self.asset_tags['AssetizedOutputfromFromWorkItem'] = str(work_item.id)
        if self.total_items_watched() == 0:
            raise ValueError("You must specify at least one item to watch")

        if len(self.file_patterns) == 0:
            logger.info("No file pattern specified. Setting to default pattern '**' to assetize all outputs")
            self.file_patterns.append("**")
        current_dir = os.path.abspath(os.path.dirname(__file__))
        self.asset_files.add_file(os.path.join(current_dir, 'assetize_ssmt_script.py'))
        self.__pickle_pre_run()
        self.__pickle_filter_func()
        self.command = self.create_command()
        user_logger.info("Creating Watcher")

    def __ensure_all_dependencies_created(self, platform: IPlatform):
        for item_type in ['related_experiments', 'related_simulations', 'related_work_items']:
            items = getattr(self, item_type)
            for item in items:
                if item.status is None:
                    if isinstance(item, IRunnableEntity):
                        item.run(platform=platform)
                    # this should only be sim in this branch
                    else:
                        item.parent.run(platform=platform)

    def total_items_watched(self) -> int:
        total = 0
        for item_type in ['related_experiments', 'related_simulations', 'related_work_items']:
            total += len(getattr(self, item_type))
        return total

    def run_after(self, item: Union[AssetizableItem, List[AssetizableItem]]):
        if not isinstance(item, list):
            items_to_add = [item]
        else:
            items_to_add = item
        for i in items_to_add:
            if isinstance(i, Experiment):
                self.related_experiments.append(i)
            elif isinstance(i, Simulation):
                self.related_simulations.append(i)
            elif isinstance(i, IWorkflowItem):
                self.related_work_items.append(i)
            else:
                raise ValueError("We can only assetize the output of experiments, simulations, and workitems")

    def wait(self, wait_on_done_progress: bool = True, timeout: int = None, refresh_interval=None, platform: 'IPlatform' = None):
        # wait on related items before we wait on our item
        p = super()._check_for_platform_from_context(platform)
        opts = dict(wait_on_done_progress=wait_on_done_progress, timeout=timeout, refresh_interval=refresh_interval, platform=platform)
        self.__wait_on_children(**opts)

        super().wait(**opts)

    def __wait_on_children(self, **opts):
        for item_type in ['related_experiments', 'related_simulations', 'related_work_items']:
            items = getattr(self, item_type)
            for item in items:
                if isinstance(item, IRunnableEntity):
                    item.wait(**opts)
                # this should only be sim in this branch
                else:
                    item.parent.wait(**opts)
