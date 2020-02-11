"""
This script is executed as entrypoint in the docker SSMT worker.
Its role is to collect the experiment ids and analyzers and run the analysis.
"""
import pickle
from pydoc import locate
import os
import sys

try:
    # use idmtools image
    from idmtools.analysis.analyze_manager import AnalyzeManager
except ImportError:
    # use dtk-tools image
    from simtools.Analysis.AnalyzeManager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception(
            "The script needs to be called with `python platform_analysis_bootstrap.py <experiment_ids> <analyzers>.\n{}".format(
                " ".join(sys.argv)))

    # Get the experiments and analyzers
    experiments = sys.argv[1].split(",")

    # load analyzer args pickle file
    analyzer_config = pickle.load(open(r"analyzer_args.pkl", 'rb'))

    # Create analyzers
    analyzers = []
    for analyzer in sys.argv[2].split(","):
        A = locate(analyzer)
        a = A(**analyzer_config[analyzer])
        analyzers.append(a)

    if not all(analyzers):
        raise Exception("Not all analyzers could be found...\n{}".format(",".join(analyzers)))

    am = AnalyzeManager(exp_list=experiments, analyzers=analyzers)
    am.analyze()
