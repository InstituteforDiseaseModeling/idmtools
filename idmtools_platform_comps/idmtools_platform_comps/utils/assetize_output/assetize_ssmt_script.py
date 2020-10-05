import glob
import sys
from logging import getLogger, DEBUG
import humanfriendly
import re
from COMPS.Data.Simulation import SimulationState
from COMPS.Data.WorkItem import WorkItemState
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
import uuid
from tqdm import tqdm
from typing import List, Tuple, Set, Dict, Callable, Pattern
import os
import argparse
from COMPS import Client
from COMPS.Data import Experiment, QueryCriteria, AssetCollection, AssetCollectionFile, WorkItem, Simulation, CommissionableEntity


logger = getLogger(__name__)
user_logger = getLogger('user')
# Our Asset Tuple we use to gather data on files
# The format is Source Filename, Destination Filename, Checksum, and then Filesize
AssetTuple = Tuple[str, str, uuid.UUID, int]
SetOfAssets = Set[AssetTuple]
# Define our function that can be used as callbacks for filtering entities
EntityFilterFunc = Callable[[CommissionableEntity.CommissionableEntity], bool]


def gather_files(directory: str, file_patterns: List[str], exclude_patterns: List[Pattern] = None, assets: bool = False, prefix: str = None) -> SetOfAssets:
    """
    Gather file_list

    Args:
        directory: Directory to gather from
        file_patterns: List of file patterns
        exclude_patterns: List of patterns to exclude
        assets: Should assets be included
        prefix: Prefix for file_list

    Returns:

    """
    from idmtools.utils.hashing import calculate_md5
    file_list = set()
    # Loop through our patterns
    for pattern in file_patterns:
        # User glob to search each directory using the pattern. We also do full recursion here
        for file in glob.glob(os.path.join(directory, pattern), recursive=True):
            # Ensure it is a file and not a directory
            if os.path.isfile(file):
                # Create our shortname. This will remove the base directory from the file. Eg
                # If are scanning C:\ABC\, the file C:\ABC\DEF\123.txt will be DEF\123.txt
                short_name = file.replace(directory + os.path.sep, "")
                # Setup destination name which is just joining prefix if it exists
                dest_name = os.path.join(prefix if prefix else '', short_name)
                filesize = os.stat(file).st_size
                # Process assets separately than regular files
                if short_name.startswith("Assets"):
                    if assets:
                        file_list.add((file, dest_name, uuid.UUID(calculate_md5(file)), filesize))
                else:
                    file_list.add((file, dest_name, uuid.UUID(calculate_md5(file)), filesize))

    # Now strip file that match exclude patterns. We do this after since the regular expressions here are a bit more expensive, so a we are at the
    # minimum possible files we must scan as this point. We did possible calculate extra md5s here
    return set([f for f in file_list if not is_file_excluded(f[0], exclude_patterns)])


def is_file_excluded(file_details: str, exclude_patterns: List[Pattern]) -> bool:
    """

    Args:
        file_details: File to filter
        exclude_patterns: List of file patterns to exclude

    Returns:
        True is file is excluded
    """
    for pattern in exclude_patterns:
        if pattern.match(file_details):
            return True
    return False


def gather_files_from_related(work_item: WorkItem, file_patterns: List[str], exclude_patterns: List[str], assets: bool, simulation_prefix_format_str: str, work_item_prefix_format_str: str, entity_filter_func: EntityFilterFunc) -> SetOfAssets:
    """
    Gather files from different related entities

    Args:
        work_item: Work item to gather from
        file_patterns: List of File Patterns
        exclude_patterns: List of Exclude patterns
        assets: Should items be gathered from Assets Directory
        simulation_prefix_format_str: Format prefix format string for Simulations
        work_item_prefix_format_str: Format prefix format string for WorkItem

    Returns:
        Set of File Tuples in format Filename, Destination Name, and Checksum
    """
    file_list = set()
    # Setup threading work using a future list and a ThreadPoolExecutor
    futures = []
    pool = ThreadPoolExecutor()
    exclude_patterns_compiles = strs_to_regular_expressions(exclude_patterns)

    # Start with experiments since they are the most complex portion
    experiments: List[Experiment] = work_item.get_related_experiments()
    for experiment in experiments:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Running filter on {experiment.name}/{experiment.id}')
        if entity_filter_func(experiment):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading simulations for filter on {experiment.name}/{experiment.id}')
            # Fetch simulations with the hpc_jobs criteria. This allows us to lookup the directory
            simulations = experiment.get_simulations(QueryCriteria().select_children('hpc_jobs'))
            if len(simulations) > 0:
                # If we should gather assets, use the first simulation. It means we will duplicate some work, but the set will filter out duplicated
                if assets:
                    # find the first simulation we can use to gather assets from
                    i = 0
                    while not entity_filter_func(simulations[i]) and i < len(simulations):
                        i += 1
                    simulation = simulations[i]
                    if logger.isEnabledFor(DEBUG):
                        logger.debug(f'Loading assets for {experiment.name} from simulation {simulation.id}')
                    # create prefix from the format var
                    prefix = simulation_prefix_format_str.format(simulation=simulation, experiment=experiment) if simulation_prefix_format_str else None
                    futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix))
                # Loop through each simulation and queue it up for file matching
                for simulation in simulations:
                    if entity_filter_func(simulation):
                        if logger.isEnabledFor(DEBUG):
                            logger.debug(f'Loading outputs from Simulation {simulation.id} with status of {simulation.state}')
                        # create prefix from the format var
                        prefix = simulation_prefix_format_str.format(simulation=simulation) if simulation_prefix_format_str else None
                        if logger.isEnabledFor(DEBUG):
                            logger.debug(f"Prefix: {prefix}")
                            logger.debug(f"HPC Jobs: {simulation.hpc_jobs}")
                        # When loading simulations, we always exclude Assets. This are some edge cases we could be missing here
                        # When simulations do not have the same AssetCollections throughout. For now, we will document this as a limitation until it is needed
                        futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=False, prefix=prefix))

    # Here we loop through simulations directly added by user. We do not
    simulations: List[Simulation] = work_item.get_related_simulations()
    for simulation in simulations:
        if entity_filter_func(simulation):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading outputs from Simulation {simulation.id} with status of {simulation.state}')
            prefix = simulation_prefix_format_str.format(simulation=simulation) if simulation_prefix_format_str else None
            futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix))

    # Here we loop through workitems
    work_items: List[WorkItem] = work_item.get_related_work_items()
    for related_work_item in work_items:
        if entity_filter_func(related_work_item):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading outputs from WorkItem {related_work_item.name} - {related_work_item.id}')
            prefix = work_item_prefix_format_str.format(work_item=related_work_item) if work_item_prefix_format_str else None
            futures.append(pool.submit(gather_files, directory=related_work_item.working_directory, afile_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix))

    # Now wait until scanning items has completed
    for future in tqdm(as_completed(futures), total=len(futures), desc="Filtering relations for files"):
        file_list.update(future.result())

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Total Files found: {len(file_list)}")
    return file_list


def strs_to_regular_expressions(exclude_patterns: List[str], ignore_case: bool = True) -> List[Pattern]:
    """
    Convert a list strings to regular expressions. The function assumes the strings are not true regular expressions, but instead are wildcards

    Args:
        exclude_patterns: Exclude patterns
        ignore_case: Should the regular expression ignore case?

    Returns:
        List of Regular Expressions
    """
    exclude_patterns_compiles: List[Pattern] = []
    for pattern in exclude_patterns:
        pattern_str = f'.*{pattern.replace("*", ".*")}.*'
        exclude_patterns_compiles.append(re.compile(pattern_str, re.IGNORECASE if ignore_case else None))
    return exclude_patterns_compiles


def create_asset_collection(file_list: SetOfAssets, asset_tags: Dict[str, str]):
    """

    Args:
        file_list:
        asset_tags: Dict of tags to add to final asset

    Returns:

    """
    asset_collection = AssetCollection()
    asset_collection.set_tags(asset_tags)
    # Maps checksum to AssetCollectionFile and the path on disk to file
    asset_collection_map: Dict[uuid.UUID, Tuple[AssetCollectionFile, str]] = dict()
    for file in file_list:
        fn = os.path.basename(file[1])
        acf = AssetCollectionFile(file_name=fn, relative_path=file[1].replace(fn, "").strip("/"), md5_checksum=file[2])
        asset_collection_map[file[2]] = (acf, file[0])
        asset_collection.add_asset(acf)

    # do initial save to see what assets are in comps
    missing_files = asset_collection.save(return_missing_files=True)
    if missing_files:
        user_logger.info(f"{len(missing_files)} not currently in COMPS as Assets")

        ac2 = AssetCollection()
        new_files = 0
        total_to_upload = 0
        for checksum, asset_details in asset_collection_map.items():
            if checksum in missing_files:
                new_files += 1
                total_to_upload += asset_details[3]
                acf = AssetCollectionFile(file_name=asset_details[0].file_name, relative_path=asset_details[0].relative_path)
                ac2.add_asset(acf, asset_details[1])
            else:
                ac2.add_asset(asset_details[0])
        user_logger.info(f"Saving {new_files} totaling {humanfriendly.format_size(total_to_upload)} assets to comps")
        asset_collection.set_tags(asset_tags)
        ac2.save()
        asset_collection = ac2
    return asset_collection


def ensure_items_are_ready(work_item: WorkItem):
    experiments: List[Experiment] = work_item.get_related_experiments()
    for experiment in experiments:
        simulations: List[Simulation] = experiment.get_simulations()
        for simulation in simulations:
            logger.debug(f'Loading outputs from Simulation {simulation.id} with status of {simulation.state}')
            if simulation.state not in [SimulationState.Failed, SimulationState.Canceled, SimulationState.Succeeded]:
                user_logger.info(f"Pausing work until {simulation.id} is done")
                sys.exit(206)
    work_items: List[WorkItem] = work_item.get_related_work_items()

    for simulation in work_item.get_related_simulations():
        if simulation.state not in [SimulationState.Failed, SimulationState.Canceled, SimulationState.Succeeded]:
            user_logger.info(f"Pausing work until {simulation.id} is done")
            sys.exit(206)

    for related_work_item in work_items:
        if related_work_item.state not in [WorkItemState.Succeeded, WorkItemState.Canceled, WorkItemState.Failed]:
            user_logger.info(f"Pausing work until {related_work_item.id} is done")
            sys.exit(206)


def get_argument_parser():
    parser = argparse.ArgumentParser("Assetize Output script")
    parser.add_argument("--file-pattern", action='append', help="File Pattern to Assetize")
    parser.add_argument("--asset-tag", action='append', help="List of tags as value pairs. Eg: ABC=123")
    parser.add_argument("--exclude-pattern", action='append', default=None, help="Exclude File Pattern to Assetize")
    parser.add_argument("--simulation-prefix-format-str", default="{simulation.id}", help="Format for prefix of outputs from simulations. Defaults to the simulation id. When setting, you have access to the full simulation object. "
                                                                                          "If you are filtering an experiment, you have also have access to experiment object")
    parser.add_argument("--no-simulation-prefix", default=False, action='store_true', help="No simulation prefix. Be careful because this could cause file collisions")
    parser.add_argument("--work-item-prefix-format-str", default=None, help="Format for prefix of workitem outputs. Defaults to None. Useful when combining outputs of multiple work-items")
    parser.add_argument("--assets", default=False, action='store_true', help="Include Assets")
    parser.add_argument("--verbose", default=False, action="store_true", help="Verbose logging")
    parser.add_argument("--pre-run-func", default=None,  action='append', help="List of function to run before starting analysis. Useful to load packages up in docker container before run")
    parser.add_argument("--entity-filter-func", default=None, help="Name of function that can be used to filter items")

    return parser


if __name__ == "__main__":
    parser = get_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        # set to debug before loading idmtools
        os.environ['IDM_TOOLS_DEBUG'] = '1'
        os.environ['IDM_TOOLS_CONSOLE_LOGGING'] = '1'
        # Import idmtools here to enable logging
        from idmtools import __version__
        logger.debug(f"Using idmtools {__version__}")
        logger.debug(f"Args: {args}")
    else:
        # setup logging by importing
        from idmtools import __version__
    if args.pre_run_func:
        import pre_run
        for pre_run_func in args.pre_run_func:
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Calling PreRunFunc: {pre_run_func}")
            getattr(pre_run, args.pre_run_func)()

    # set a default filter function that returns true if none are set
    if args.entity_filter_func:
        import entity_filter_func
        entity_filter_func = getattr(entity_filter_func, args.entity_filter_func)
    else:
        entity_filter_func = lambda x: True

    # load the work item
    client = Client()
    client.login(os.environ['COMPS_SERVER'])
    wi = WorkItem.get(os.environ['COMPS_WORKITEM_GUID'])
    asset_tags = dict()
    for tag in args.asset_tag:
        name, value = tag.split("=")
        asset_tags[name] = value

    ensure_items_are_ready(wi)
    files = gather_files_from_related(
        wi, file_patterns=args.file_pattern, exclude_patterns=args.exclude_pattern if args.exclude_pattern else [], assets=args.assets,
        work_item_prefix_format_str=args.work_item_prefix_format_str,
        simulation_prefix_format_str=args.simulation_prefix_format_str if not args.no_simulation_prefix else None,
        entity_filter_func=entity_filter_func
    )

    ac = create_asset_collection(files, asset_tags=asset_tags)
    with open('asset_collection.id', 'w') as o:
        user_logger.info(ac.id)
        o.write(str(ac.id))
