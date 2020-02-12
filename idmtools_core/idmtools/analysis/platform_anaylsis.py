import inspect
import os
import pickle
import tempfile

from idmtools.assets.file_list import FileList
from idmtools_platform_comps.ssmt_work_items.comps_workitems import SSMTWorkItem


class PlatformAnalysis:

    def __init__(self, platform, experiment_ids, analyzers, analyzers_args=None, analysis_name='WorkItem Test',
                 tags=None,
                 additional_files=None, asset_collection_id=None, asset_files=FileList()):
        self.platform = platform
        self.experiment_ids = experiment_ids
        self.analyzers = analyzers
        self.analyzers_args = analyzers_args
        self.analysis_name = analysis_name
        self.tags = tags
        self.additional_files = additional_files or FileList()
        self.asset_collection_id = asset_collection_id
        self.asset_files = asset_files
        self.wi = None

        self.validate_args()

    def analyze(self, check_status=True):
        # Add the platform_analysis_bootstrap.py file to the collection
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.additional_files.add_file(os.path.join(dir_path, "platform_analysis_bootstrap.py"))

        # If there is a idmtools.ini, send it along
        if os.path.exists(os.path.join(os.getcwd(), "idmtools.ini")):
            self.additional_files.add_file(os.path.join(os.getcwd(), "idmtools.ini"))

        # build analyzer args dict
        args_dict = {}
        a_args = zip(self.analyzers, self.analyzers_args)
        for a, g in a_args:
            args_dict[f"{inspect.getmodulename(inspect.getfile(a))}.{a.__name__}"] = g

        # save pickle file as a temp file
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, "analyzer_args.pkl")
        pickle.dump(args_dict, open(temp_file, 'wb'))

        # Add analyzer args pickle as additional file
        self.additional_files.add_file(temp_file)

        # Add all the analyzers files
        for a in self.analyzers:
            self.additional_files.add_file(inspect.getfile(a))

        # Create the command
        command = "python platform_analysis_bootstrap.py"
        # Add the experiments
        command += " {}".format(",".join(self.experiment_ids))
        # Add the analyzers
        command += " {}".format(",".join(f"{inspect.getmodulename(inspect.getfile(a))}.{a.__name__}"
                                         for a in self.analyzers))

        self.wi = SSMTWorkItem(item_name=self.analysis_name, command=command, tags=self.tags,
                               user_files=self.additional_files, asset_collection_id=self.asset_collection_id,
                               asset_files=self.asset_files, related_experiments=self.experiment_ids)

        # Run the workitem
        self.wi.run(True, platform=self.platform)

        # remove temp file
        os.remove(temp_file)

    def validate_args(self):
        if self.analyzers_args is None:
            self.analyzers_args = [{}] * len(self.analyzers)
            return

        self.analyzers_args = [g if g is not None else {} for g in self.analyzers_args]

        if len(self.analyzers_args) < len(self.analyzers):
            self.analyzers_args = self.analyzers_args + [{}] * (len(self.analyzers) - len(self.analyzers_args))
            return

        if len(self.analyzers) < len(self.analyzers_args):
            print("two list 'analyzers' and 'analyzers_args' must have the same length.")
            exit()

    def get_work_item(self):
        return self.wi
