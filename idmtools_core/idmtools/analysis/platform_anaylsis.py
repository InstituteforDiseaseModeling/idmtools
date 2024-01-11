"""
Platform Analysis is a wrapper to allow execution of analysis through SSMT vs Locally.

Running remotely has great advantages over local execution with the biggest being more compute resources and less data transfer.
Platform Analysis tries to make the process of running remotely similar to local execution.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import re
from typing import List, Callable, Union, Type, Dict, Any
import inspect
import os
import pickle
from logging import getLogger, DEBUG
from idmtools.assets import Asset, AssetCollection
from idmtools.assets.file_list import FileList
from idmtools.config import IdmConfigParser
from idmtools.entities import IAnalyzer
from idmtools.entities.iplatform import IPlatform
from idmtools.entities.iplatform_default import AnalyzerManagerPlatformDefault
from idmtools.utils.info import get_help_version_url

logger = getLogger(__name__)
user_logger = getLogger('user')


class PlatformAnalysis:
    """
    PlatformAnalysis allows remote Analysis on the server.

    See Also:
        :py:class:`idmtools.analysis.analyze_manager.AnalyzeManager`
    """

    def __init__(self, platform: IPlatform, analyzers: List[Type[IAnalyzer]],
                 experiment_ids: List['str'] = [], simulation_ids: List['str'] = [], work_item_ids: List['str'] = [],
                 analyzers_args=None, analysis_name: str = 'WorkItem Test', tags=None,
                 additional_files: Union[FileList, AssetCollection, List[str]] = None, asset_collection_id=None,
                 asset_files: Union[FileList, AssetCollection, List[str]] = None, wait_till_done: bool = True,
                 idmtools_config: str = None, pre_run_func: Callable = None, wrapper_shell_script: str = None,
                 verbose: bool = False, extra_args: Dict[str, Any] = None):
        """
        Initialize our platform analysis.

        Args:
            platform: Platform
            experiment_ids: Experiment ids
            simulation_ids: Simulation ids
            work_item_ids: WorkItem ids
            analyzers: Analyzers to run
            analyzers_args: Arguments for our analyzers
            analysis_name: Analysis name
            tags: Tags for the workitem
            additional_files: Additional files for server analysis
            asset_collection_id: Asset Collection to use
            asset_files: Asset files to attach
            wait_till_done: Wait until analysis is done
            idmtools_config: Optional path to idmtools.ini to use on server. Mostly useful for development
            pre_run_func: A function (with no arguments) to be executed before analysis starts on the remote server
            wrapper_shell_script: Optional path to a wrapper shell script. This script should redirect all arguments to command passed to it. Mostly useful for development purposes
            verbose: Enables verbose logging remotely
            extra_args: Optional extra arguments to pass to AnalyzerManager on the server side. See :meth:`~idmtools.analysis.analyze_manager.AnalyzeManager.__init__`

        See Also:
            :meth:`idmtools.analysis.analyze_manager.AnalyzeManager.__init__`
        """
        self.platform = platform
        self.experiment_ids = experiment_ids or []
        self.simulation_ids = simulation_ids or []
        self.work_item_ids = work_item_ids or []
        self.analyzers = analyzers
        self.analyzers_args = analyzers_args
        self.analysis_name = analysis_name
        self.tags = tags
        if isinstance(additional_files, list):
            additional_files = AssetCollection(additional_files)
        elif isinstance(additional_files, FileList):
            additional_files = additional_files.to_asset_collection()
        self.additional_files: AssetCollection = additional_files or AssetCollection()
        self.asset_collection_id = asset_collection_id
        if isinstance(asset_files, list):
            asset_files = AssetCollection(asset_files)
        elif isinstance(asset_files, FileList):
            asset_files = asset_files.to_asset_collection()
        self.asset_files: AssetCollection = asset_files or AssetCollection()
        self.wi = None
        self.wait_till_done = wait_till_done
        self.idmtools_config = idmtools_config
        self.pre_run_func = pre_run_func
        self.wrapper_shell_script = wrapper_shell_script
        self.shell_script_binary = "/bin/bash"
        self.verbose = verbose
        self.extra_args = extra_args if extra_args else dict()

        self.validate_args()

    def analyze(self, check_status=True):
        """
        Analyze remotely.

        Args:
            check_status: Should we check status

        Returns:
            None

        Notes:
            TODO: check_status is not being used
        """
        command = self._prep_analyze()

        logger.debug(f"Command: {command}")
        from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem

        ac = AssetCollection.from_id(self.asset_collection_id,
                                     platform=self.platform) if self.asset_collection_id else AssetCollection()
        ac.add_assets(self.asset_files)
        self.wi = SSMTWorkItem(name=self.analysis_name, command=command, tags=self.tags,
                               transient_assets=self.additional_files, assets=ac,
                               related_experiments=self.experiment_ids,
                               related_simulations=self.simulation_ids,
                               related_work_items=self.work_item_ids
                               )

        # Run the workitem
        self.platform.run_items(self.wi)
        if self.wait_till_done:
            self.platform.wait_till_done(self.wi)
        logger.debug(f"Status: {self.wi.status}")

    def _prep_analyze(self):
        """
        Prepare for analysis.

        Returns:
            None
        """
        # Add the platform_analysis_bootstrap.py file to the collection
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.additional_files.add_or_replace_asset(os.path.join(dir_path, "platform_analysis_bootstrap.py"))
        # check if user gave us an override to idmtools config
        if self.idmtools_config:
            self.additional_files.add_or_replace_asset(self.idmtools_config)
        else:
            # look for one from idmtools.
            config_path = IdmConfigParser.get_config_path()
            if config_path and os.path.exists(config_path):
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Adding config file: {config_path}")
                self.additional_files.add_or_replace_asset(config_path)

        # build analyzer args dict
        args_dict = {}
        a_args = zip(self.analyzers, self.analyzers_args)
        for a, g in a_args:
            args_dict[f"{inspect.getmodulename(inspect.getfile(a))}.{a.__name__}"] = g
        if self.pre_run_func:
            self.__pickle_pre_run()
        # save pickle file as a temp file
        self.__pickle_analyzers(args_dict)

        # Add all the analyzers files
        for a in self.analyzers:
            self.additional_files.add_or_replace_asset(inspect.getfile(a))

        # add our extra arguments for analyzer manager
        if 'max_workers' not in self.extra_args:
            am_defaults: List[AnalyzerManagerPlatformDefault] = self.platform.get_defaults_by_type(
                AnalyzerManagerPlatformDefault)
            if len(am_defaults):
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Setting max workers to comps default of: {am_defaults[0].max_workers}")
                self.extra_args['max_workers'] = am_defaults[0].max_workers

        # Create the command
        command = ''
        if self.wrapper_shell_script:
            self.additional_files.add_or_replace_asset(self.wrapper_shell_script)
            command += f'{self.shell_script_binary} {os.path.basename(self.wrapper_shell_script)} '
        command += "python3 platform_analysis_bootstrap.py"
        # Add the experiments
        if self.experiment_ids:
            command += f' --experiment-ids {",".join(self.experiment_ids)}'
        # Add the simulations
        if self.simulation_ids:
            command += f' --simulation-ids {",".join(self.simulation_ids)}'
        # Add the work items
        if self.work_item_ids:
            command += f' --work-item-ids {",".join(self.work_item_ids)}'
        # Add the analyzers
        command += " --analyzers {}".format(
            ",".join(f"{inspect.getmodulename(inspect.getfile(a))}.{a.__name__}" for a in self.analyzers))

        if self.pre_run_func:
            command += f" --pre-run-func {self.pre_run_func.__name__}"

        # Pickle the extra args
        if len(self.extra_args):
            from idmtools.analysis.analyze_manager import AnalyzeManager
            argspec = inspect.signature(AnalyzeManager.__init__)
            for argname, value in self.extra_args.items():
                if argname not in argspec.parameters:
                    raise ValueError(
                        f"AnalyzerManager does not support the argument {argname}. Valid args are {' '.join([str(s) for s in argspec.parameters.keys()])}. See {get_help_version_url('idmtools.analysis.analyze_manager.html#idmtools.analysis.analyze_manager.AnalyzeManager')} for a valid list of arguments.")
                # TODO do type validations later
            self.additional_files.add_or_replace_asset(
                Asset(filename="extra_args.pkl", content=pickle.dumps(self.extra_args)))
            command += " --analyzer-manager-args-file extra_args.pkl"

        self.__pickle_platform_args()
        command += " --platform-args platform_args.pkl"

        # Add platform
        ssmt_config_block = f"{self.platform._config_block}_SSMT"
        command += " --block {}".format(ssmt_config_block)
        if self.verbose:
            command += " --verbose"

        return command

    def __pickle_analyzers(self, args_dict):
        """
        Pickle our analyzers and add as assets.

        Args:
            args_dict: Analyzer and args

        Returns:
            None
        """
        self.additional_files.add_or_replace_asset(Asset(filename='analyzer_args.pkl', content=pickle.dumps(args_dict)))

    def __pickle_pre_run(self):
        """
        Pickle objects before we run and add items as assets.

        Returns:
            None
        """
        source = inspect.getsource(self.pre_run_func).splitlines()
        space_base = 0
        while source[0][space_base] == " ":
            space_base += 1
        replace_expr = re.compile("^[ ]{" + str(space_base) + "}")
        new_source = []
        for line in source:
            new_source.append(replace_expr.sub("", line))

        self.additional_files.add_or_replace_asset(Asset(filename="pre_run.py", content="\n".join(new_source)))

    def __pickle_platform_args(self):
        """
        Pickle platform args and add as assets.

        Returns:
            None
        """
        # Pickle the platform args
        platform_kwargs = self.platform._kwargs
        platform_kwargs["missing_ok"] = self.platform._missing_ok
        self.additional_files.add_or_replace_asset(
            Asset(filename="platform_args.pkl", content=pickle.dumps(platform_kwargs)))

    def validate_args(self):
        """
        Validate arguments for the platform analysis and analyzers.

        Returns:
            None
        """
        if self.analyzers_args is None:
            self.analyzers_args = [{}] * len(self.analyzers)
            return

        self.analyzers_args = [g if g is not None else {} for g in self.analyzers_args]

        if len(self.analyzers_args) < len(self.analyzers):
            self.analyzers_args = self.analyzers_args + [{}] * (len(self.analyzers) - len(self.analyzers_args))
            return

        if len(self.analyzers) < len(self.analyzers_args):
            user_logger.error("two list 'analyzers' and 'analyzers_args' must have the same length.")
            exit()

    def get_work_item(self):
        """
        Get work item being using to run analysis job on server.

        Returns:
            Workflow item
        """
        return self.wi
