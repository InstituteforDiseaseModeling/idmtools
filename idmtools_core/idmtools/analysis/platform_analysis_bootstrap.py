"""
This script is executed as entrypoint in the docker SSMT worker.

Its role is to collect the experiment ids and analyzers and run the analysis.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import argparse
import os
import pickle
import sys
from pydoc import locate


sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("PlatformAnalysis bootstrap")
    parser.add_argument("--experiment-ids", help="A comma separated list of experiments to analyze")
    parser.add_argument("--analyzers", help="Commas separated list of analyzers")
    parser.add_argument("--block", help="Configuration block to use")
    parser.add_argument("--verbose", default=False, action="store_true", help="Verbose logging")
    parser.add_argument("--pre-run-func", default=None, help="List of function to run before starting analysis. Useful to load packages up in docker container before run")

    args = parser.parse_args()
    if args.verbose:
        # enable verbose logging before we load idmtools
        os.environ['IDMTOOLS_LOGGING_LEVEL'] = 'DEBUG'
        os.environ['IDMTOOLS_LOGGING_CONSOLE'] = '1'

    # delay loading idmtools so we can change log level through environment
    from idmtools.core import ItemType
    from idmtools.core.platform_factory import Platform
    from idmtools.analysis.analyze_manager import AnalyzeManager

    if args.pre_run_func:
        import pre_run
        getattr(pre_run, args.pre_run_func)()

    # Get the experiments, analyzers and platform
    experiments = args.experiment_ids.split(",")
    experiment_ids = []
    for experiment in experiments:
        experiment_tuple = (experiment, ItemType.EXPERIMENT)
        experiment_ids.append(experiment_tuple)

    # load analyzer args pickle file
    analyzer_config = pickle.load(open(r"analyzer_args.pkl", 'rb'))

    # Create analyzers
    analyzers = []
    for analyzer in args.analyzers.split(","):
        A = locate(analyzer)
        a = A(**analyzer_config[analyzer])
        analyzers.append(a)

    if not all(analyzers):
        raise Exception("Not all analyzers could be found...\n{}".format(",".join(analyzers)))

    # get platform
    platform = Platform(args.block)
    am = AnalyzeManager(platform=platform, ids=experiment_ids, analyzers=analyzers)
    am.analyze()
