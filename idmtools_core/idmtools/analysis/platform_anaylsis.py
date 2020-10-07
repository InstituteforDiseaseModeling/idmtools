import re
from typing import List, Callable
import inspect
import os
import pickle
from logging import getLogger, DEBUG
from idmtools.assets import Asset
from idmtools.assets.file_list import FileList
from idmtools.config import IdmConfigParser
from idmtools.entities import IAnalyzer
from idmtools.entities.iplatform import IPlatform

logger = getLogger(__name__)
user_logger = getLogger('user')


class PlatformAnalysis:

    def __init__(self, platform: IPlatform, experiment_ids: List['str'], analyzers: List[IAnalyzer], analyzers_args=None, analysis_name: str = 'WorkItem Test', tags=None, additional_files=None, asset_collection_id=None, asset_files=FileList(), wait_till_done: bool = True,
                 idmtools_config: str = None, pre_run_func: Callable = None, wrapper_shell_script: str = None, verbose: bool = False):
        """

        Args:
            platform: Platform
            experiment_ids:
            analyzers:
            analyzers_args:
            analysis_name:
            tags:
            additional_files:
            asset_collection_id:
            asset_files:
            wait_till_done:
            idmtools_config: Optional path to idmtools.ini to use on server. Mostly useful for development
            pre_run_func: A function (with no arguments) to be executed before analysis starts on the remote server
            wrapper_shell_script: Optional path to a wrapper shell script. This script should redirect all arguments to command passed to it. Mostly useful for development purposes
            verbose: Enables verbose logging remotely

        """
        self.platform = platform
        self.experiment_ids = experiment_ids
        self.analyzers = analyzers
        self.analyzers_args = analyzers_args
        self.analysis_name = analysis_name
        self.tags = tags
        if isinstance(additional_files, list):
            additional_files = self.__files_to_filelist(additional_files)
        self.additional_files = additional_files or FileList()
        self.asset_collection_id = asset_collection_id
        if isinstance(asset_files, list):
            asset_files = self.__files_to_filelist(asset_files)
        self.asset_files = asset_files
        self.wi = None
        self.wait_till_done = wait_till_done
        self.idmtools_config = idmtools_config
        self.pre_run_func = pre_run_func
        self.wrapper_shell_script = wrapper_shell_script
        self.shell_script_binary = "/bin/bash"
        self.verbose = verbose

        self.validate_args()

    def __files_to_filelist(self, additional_files):
        new_add_files = FileList()
        for file in additional_files:
            if isinstance(file, str):
                new_add_files.add_file(file)
            else:
                new_add_files.add_asset_file(file)
        additional_files = new_add_files
        return additional_files

    def analyze(self, check_status=True):
        command = self._prep_analyze()

        logger.debug(f"Command: {command}")
        from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem
        self.wi = SSMTWorkItem(item_name=self.analysis_name, command=command, tags=self.tags,
                               user_files=self.additional_files, asset_collection_id=self.asset_collection_id,
                               asset_files=self.asset_files, related_experiments=self.experiment_ids)

        # Run the workitem
        self.platform.run_items(self.wi)
        if self.wait_till_done:
            self.platform.wait_till_done(self.wi)
        logger.debug(f"Status: {self.wi.status}")

    def _prep_analyze(self):
        # Add the platform_analysis_bootstrap.py file to the collection
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.additional_files.add_file(os.path.join(dir_path, "platform_analysis_bootstrap.py"))
        # check if user gave us an override to idmtools config
        if self.idmtools_config:
            self.additional_files.add_file(self.idmtools_config)
        else:
            # look for one from idmtools.
            config_path = IdmConfigParser.get_config_path()
            if config_path and os.path.exists(IdmConfigParser.get_config_path()):
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Adding {config_path} ini")
                self.additional_files.add_file(config_path)

        if self.wrapper_shell_script:
            self.additional_files.add_file(os.path.join(self.wrapper_shell_script))
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
            self.additional_files.add_file(inspect.getfile(a))
        # Create the command
        command = ''
        if self.wrapper_shell_script:
            self.additional_files.add_file(self.wrapper_shell_script)
            command += f'{self.shell_script_binary} {os.path.basename(self.wrapper_shell_script)} '
        command += "python platform_analysis_bootstrap.py"
        # Add the experiments
        command += f' --experiment-ids {",".join(self.experiment_ids)}'
        # Add the analyzers
        command += " --analyzers {}".format(",".join(f"{inspect.getmodulename(inspect.getfile(a))}.{a.__name__}" for a in self.analyzers))

        if self.pre_run_func:
            command += f" --pre-run-func {self.pre_run_func.__name__}"
        # Add platform
        command += " --block {}".format(IdmConfigParser._block)
        if self.verbose:
            command += " --verbose"
        return command

    def __pickle_analyzers(self, args_dict):
        self.additional_files.add_asset_file(Asset(filename='analyzer_args.pkl', content=pickle.dumps(args_dict)))

    def __pickle_pre_run(self):
        source = inspect.getsource(self.pre_run_func).splitlines()
        space_base = 0
        while source[0][space_base] == " ":
            space_base += 1
        replace_expr = re.compile("^[ ]{" + str(space_base) + "}")
        new_source = []
        for line in source:
            new_source.append(replace_expr.sub("", line))

        self.additional_files.add_asset_file(Asset(filename="pre_run.py", content="\n".join(new_source)))

    def validate_args(self):
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
        return self.wi
