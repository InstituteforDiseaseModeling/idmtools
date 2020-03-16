"""
This script is executed as entrypoint in the docker SSMT worker.
Its role is to collect the experiment ids and analyzers and run the analysis.
"""
import os
import pickle
import sys
from pydoc import locate
from idmtools.core import ItemType
from idmtools.core.platform_factory import Platform
from idmtools.analysis.analyze_manager import AnalyzeManager

sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    if len(sys.argv) < 4:
        raise Exception(
            "The script needs to be called with `python platform_analysis_bootstrap.py <experiment_ids> <analyzers> "
            "platform_block.\n{}".format(" ".join(sys.argv)))

    # Get the experiments, analyzers and platform
    experiments = sys.argv[1].split(",")
    experiment_ids = []
    for experiment in experiments:
        experiment_tuple = (experiment, ItemType.EXPERIMENT)
        experiment_ids.append(experiment_tuple)

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

    # get platform
    block = sys.argv[3]
    platform = Platform(block)
    am = AnalyzeManager(platform=platform, ids=experiment_ids, analyzers=analyzers)
    am.analyze()
