"""
This script is executed as entrypoint in the docker SSMT worker.

Its role is to collect the experiment ids and analyzers and run the analysis.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import argparse
import os
import pickle
import sys
from logging import getLogger
from pydoc import locate


sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("PlatformAnalysis bootstrap")
    parser.add_argument("--experiment-ids", default=None, help="A comma separated list of experiments to analyze")
    parser.add_argument("--simulation-ids", default=None, help="A comma separated list of simulations to analyze")
    parser.add_argument("--work-item-ids", default=None, help="A comma separated list of work items to analyze")
    parser.add_argument("--analyzers", help="Commas separated list of analyzers")
    parser.add_argument("--block", help="Configuration block to use")
    parser.add_argument("--verbose", default=False, action="store_true", help="Verbose logging")
    parser.add_argument("--pre-run-func", default=None, help="List of function to run before starting analysis. Useful to load packages up in docker container before run")
    parser.add_argument("--analyzer-manager-args-file", default=None, help="Path to extra arguments for analyzer manager")
    parser.add_argument("--platform-args", default=None, help="Arguments used to create Platform")

    args = parser.parse_args()
    if args.verbose:
        # enable verbose logging before we load idmtools
        os.environ['IDMTOOLS_LOGGING_LEVEL'] = 'DEBUG'
        os.environ['IDMTOOLS_LOGGING_CONSOLE'] = '1'

    # delay loading idmtools so we can change log level through environment
    from idmtools.core import ItemType
    from idmtools.core.platform_factory import Platform
    from idmtools.analysis.analyze_manager import AnalyzeManager

    logger = getLogger('SSMT Analysis')

    if args.pre_run_func:
        import pre_run
        getattr(pre_run, args.pre_run_func)()

    item_ids = []
    # Get the experiments, analyzers and platform
    if args.experiment_ids:
        experiments = args.experiment_ids.split(",")
        for experiment in experiments:
            experiment_tuple = (experiment, ItemType.EXPERIMENT)
            item_ids.append(experiment_tuple)

    # Get the simulations, analyzers and platform
    if args.simulation_ids:
        simulations = args.simulation_ids.split(",")
        for simulation in simulations:
            simulation_tuple = (simulation, ItemType.SIMULATION)
            item_ids.append(simulation_tuple)

    # Get the experiments, analyzers and platform
    if args.work_item_ids:
        work_items = args.work_item_ids.split(",")
        for wi in work_items:
            wi_tuple = (wi, ItemType.WORKFLOW_ITEM)
            item_ids.append(wi_tuple)

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

    if args.analyzer_manager_args_file is not None:
        logger.info(f"Loading extra AnalyzerManager args from {args.analyzer_manager_args_file}")
        with open(args.analyzer_manager_args_file, 'rb') as pin:
            extra_args = pickle.load(pin)

    # load platform args pickle file
    platform_args = pickle.load(open(r"platform_args.pkl", 'rb'))

    # get platform
    platform = Platform(args.block, **platform_args)
    logger.info(f"Analyzer Manager called with the following extra arguments: {extra_args}")
    am = AnalyzeManager(platform=platform, ids=item_ids, analyzers=analyzers, **extra_args)
    am.analyze()
