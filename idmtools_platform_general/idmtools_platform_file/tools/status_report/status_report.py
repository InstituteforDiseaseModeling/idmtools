"""
This is a FilePlatform simulation status utility.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
import json
from logging import getLogger
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, TYPE_CHECKING
from idmtools.core import ItemType, EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools_platform_file.tools.status_report.utils import get_latest_experiment
from idmtools_platform_file.platform_operations.utils import FILE_MAPS

if TYPE_CHECKING:  # pragma: no cover
    from idmtools.entities.iplatform import IPlatform

user_logger = getLogger('user')


@dataclass(repr=False)
class StatusReporter:
    """
    A class to wrap the functions involved in retrieving simulations status.
    """
    platform: 'IPlatform'  # noqa F821
    scope: Tuple[str, ItemType] = field(default=None)

    _exp: Experiment = field(default=None, init=False, compare=False)
    _summary: Dict = field(default_factory=dict, init=False, compare=False)
    _report: Dict = field(default_factory=dict, init=False, compare=False)
    _pending: List = field(default_factory=list, init=False, compare=False)

    def __post_init__(self):
        self.initialize()

    def initialize(self) -> None:
        """
        Determine the experiment and build dictionary with basic info.
        Returns:
            None
        """
        if self.scope is not None:
            item = self.platform.get_item(self.scope[0], self.scope[1])
            if self.scope[1] == ItemType.SUITE:
                # Only consider the first experiment
                self._exp = item.experiments[0]
            elif self.scope[1] == ItemType.EXPERIMENT:
                self._exp = item
            else:
                raise RuntimeError('Only support Suite/Experiment.')
        else:
            exp_dic = get_latest_experiment(self.platform)
            self._exp = self.platform.get_item(exp_dic['experiment_id'], ItemType.EXPERIMENT)
            exp_dir = self.platform.get_directory_by_id(exp_dic['experiment_id'], ItemType.EXPERIMENT)
            last_suite_dir = exp_dir.parent

            user_logger.info('------------------------------')
            user_logger.info(f'last suite dir: {last_suite_dir}')
            user_logger.info(f'last experiment dir: {exp_dir}')
            user_logger.info('------------------------------')

        self._summary = dict(suite=self._exp.parent.id, experiment=self._exp.id,
                             job_directory=self.platform.job_directory)

    def apply_filters(self, status_filter: Tuple[str] = None, sim_filter: Tuple[str] = None,
                      verbose: bool = True) -> None:
        """
        Filter simulations.
        Args:
            status_filter: tuple with target status
            sim_filter: tuple with simulation id
            verbose: True/False to include simulation directory
        Returns:
            None
        """
        # Make sure we get the latest status
        self.platform.refresh_status(self._exp)

        # Filter simulations and format the results
        _simulations = self._exp.simulations
        for sim in _simulations:
            # Apply simulation filter
            if sim_filter is not None and sim.id not in sim_filter:
                continue

            sim_dir = self.platform.get_directory(sim)
            job_status_path = sim_dir.joinpath("job_status.txt")
            if not job_status_path.exists():
                self._pending.append(f"    {sim.id}")
                continue

            status = open(job_status_path).read().strip()
            # Apply status filter
            if status_filter is not None and status not in status_filter:
                continue

            # Format the results
            d = dict(status=status)
            if verbose:
                d["WorkDir"] = str(self.platform.get_directory(sim))
            self._report[sim.id] = d

    @staticmethod
    def output_definition() -> None:
        """
        Output the status definition.
        Returns:
            None
        """
        file_map = copy.deepcopy(FILE_MAPS)
        file_map.pop('None', None)
        user_logger.info('------------------------------')
        user_logger.info("STATUS DEFINITION")
        user_logger.info(f"{'0: '.ljust(20)} {file_map['0'].name}")
        user_logger.info(f"{'-1: '.ljust(20)} {file_map['-1'].name}")
        user_logger.info(f"{'100: '.ljust(20)} {file_map['100'].name}")
        user_logger.info('------------------------------')

    def output_summary(self) -> None:
        """
        Output suite/experiment id and job directory.
        Returns:
            None
        """
        if self._summary:
            user_logger.info(f"{'suite: '.ljust(20)} {self._summary['suite']}")
            user_logger.info(f"{'experiment: '.ljust(20)} {self._summary['experiment']}")
            user_logger.info(f"{'job directory: '.ljust(20)} {self._summary['job_directory']}")

    def output_results(self, status_filter: Tuple[str] = None, sim_filter: Tuple[str] = None, verbose: bool = True,
                       display: bool = True):
        """
        Output search results.
        Args:
            status_filter: status filter
            sim_filter: simulation filter
            verbose: True/False
            display: True/False

        Returns:
            None
        """
        _status_list = [v["status"] for k, v in self._report.items()]
        _sim_not_run_list = [sim for sim in self._exp.simulations if sim.status == EntityStatus.CREATED]
        _simulation_count = len(self._exp.simulations)

        # print report
        user_logger.info(f"{'status filter: '.ljust(20)} {status_filter}")
        user_logger.info(f"{'sim filter: '.ljust(20)} {sim_filter}")
        user_logger.info(f"{'verbose: '.ljust(20)} {verbose}")
        user_logger.info(f"{'display: '.ljust(20)} {display}")
        user_logger.info(f"{'Simulation Count: '.ljust(20)} {_simulation_count}")
        user_logger.info(f"{'Match Count: '.ljust(20)} {len(self._report)} ({dict(Counter(_status_list))})")
        user_logger.info(f"{'Not Running Count: '.ljust(20)} {len(_sim_not_run_list)}")

        if self._exp.status is None:
            user_logger.info(f'\nExperiment Status: {None}')
        else:
            user_logger.info(f'\nExperiment Status: {self._exp.status.name}')

    def output_status_report(self, status_filter: Tuple[str] = None, sim_filter: Tuple[str] = None,
                             verbose: bool = True, display: bool = True, display_count: int = 20) -> None:
        """
        Output simulations status with possible override parameters.
        Args:
            status_filter: tuple with target status
            sim_filter: tuple with simulation id
            verbose: True/False to include simulation directory
            display: True/False to print the searched results
            display_count: how many to print
        Returns:
            None
        """
        if status_filter is None:
            status_filter = ('0', '-1', '100')

        self.apply_filters(status_filter, sim_filter, verbose)

        self.output_summary()

        if display:
            if display_count is None or len(self._report) <= display_count:
                report_view_dict = self._report
            else:
                report_view_dict = dict(list(self._report.items())[0:display_count])
            user_logger.info(json.dumps(report_view_dict, indent=3))

        self.output_definition()

        if display and len(self._report) > display_count:
            user_logger.info(f"ONLY DISPLAY {display_count} ITEMS")

        self.output_results(status_filter, sim_filter, verbose, display)


def generate_status_report(platform: 'IPlatform', scope: Tuple[str, ItemType] = None, status_filter: Tuple[str] = None,
                           sim_filter: Tuple[str] = None, verbose: bool = True, display: bool = True,
                           display_count: int = 20) -> None:
    """
    The entry point of status viewer.
    Args:
        platform: idmtools Platform
        scope: the search base
        status_filter: tuple with target status
        sim_filter: tuple with simulation id
        verbose: True/False to include simulation directory
        display: True/False to print the search results
        display_count: how many to print
    Returns:
        None
    """
    sr = StatusReporter(scope=scope, platform=platform)
    sr.output_status_report(status_filter=status_filter, sim_filter=sim_filter, verbose=verbose, display=display,
                            display_count=display_count)
