"""idmtools ssmt file filter tools.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import argparse
import glob
import json
import os
import uuid
from collections import defaultdict
from concurrent.futures._base import as_completed, Future
from concurrent.futures.thread import ThreadPoolExecutor
from logging import DEBUG, getLogger
from pathlib import PurePath
from typing import List, Tuple, Set, Callable
import humanfriendly
from COMPS.Data import WorkItem, Experiment, Simulation, AssetCollectionFile, AssetCollection, QueryCriteria, CommissionableEntity
from COMPS.Data.Simulation import SimulationState
from COMPS.Data.WorkItem import RelationType
from tabulate import tabulate
from tqdm import tqdm
from idmtools_platform_comps.utils.file_filter_workitem import FilenameFormatFunction

try:
    from common import setup_verbose
except (FileNotFoundError, ImportError):
    from idmtools_platform_comps.utils.ssmt_utils.common import setup_verbose

logger = getLogger(__name__)
user_logger = getLogger('user')
# Our Asset Tuple we use to gather data on files
# The format is Source Filename, Destination Filename, Checksum, and then Filesize
AssetTuple = Tuple[str, str, uuid.UUID, int]
SetOfAssets = Set[AssetTuple]
# Store the Done State
DONE_STATE = [SimulationState.Failed, SimulationState.Canceled, SimulationState.Succeeded]
HPC_JOBS_QUERY = QueryCriteria().select_children(['tags', 'hpc_jobs']).orderby('date_created desc')

# Define our function that can be used as callbacks for filtering entities
EntityFilterFunc = Callable[[CommissionableEntity.CommissionableEntity], bool]


def get_common_parser(app_description):
    """Creates a get common argument parser used with file filter function."""
    parser = argparse.ArgumentParser(app_description)
    parser.add_argument("--file-pattern", nargs="+", help="File Pattern to Filter")
    parser.add_argument("--exclude-pattern", default=None, nargs="+", help="Exclude File Pattern to Filter")
    parser.add_argument(
        "--simulation-prefix-format-str", default="{simulation.id}",
        help="Format for prefix of outputs from simulations. Defaults to the simulation id. When setting, you have access to the full simulation object. "
             "If you are filtering an experiment, you have also have access to experiment object"
    )
    parser.add_argument("--no-simulation-prefix", default=False, action='store_true', help="No simulation prefix. Be careful because this could cause file collisions")
    parser.add_argument("--work-item-prefix-format-str", default=None, help="Format for prefix of workitem outputs. Defaults to None. Useful when combining outputs of multiple work-items")
    parser.add_argument("--assets", default=False, action='store_true', help="Include Assets")
    parser.add_argument("--verbose", default=False, action="store_true", help="Verbose logging")
    parser.add_argument("--pre-run-func", default=None, action='append', help="List of function to run before starting analysis. Useful to load packages up in docker container before run")
    parser.add_argument("--entity-filter-func", default=None, help="Name of function that can be used to filter items")
    parser.add_argument("--filename-format-func", default=None, help="Name of function that can be used to format filenames")
    parser.add_argument("--dry-run", default=False, action="store_true", help="Find files, but don't add")
    return parser


def gather_files(directory: str, file_patterns: List[str], exclude_patterns: List[str] = None, assets: bool = False, prefix: str = None, filename_format_func: FilenameFormatFunction = None) -> SetOfAssets:
    """
    Gather file_list.

    Args:
        directory: Directory to gather from
        file_patterns: List of file patterns
        exclude_patterns: List of patterns to exclude
        assets: Should assets be included
        prefix: Prefix for file_list
        filename_format_func: Function that can format the filename

    Returns:
        Return files that match patterns.
    """
    from idmtools.utils.hashing import calculate_md5
    file_list = set()
    # Loop through our patterns
    for pattern in file_patterns:
        # User glob to search each directory using the pattern. We also do full recursion here

        sd = os.path.join(directory, pattern)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Looking for files with pattern {sd}')
        for file in glob.iglob(sd, recursive=True):
            # Ensure it is a file and not a directory
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'{file.encode("ascii", "ignore").decode("utf-8")} matching pattern. Is Dir: {os.path.isdir(file)}. Is Link: {os.path.islink(file)}')
            if os.path.isfile(file):
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f'Found file {file.encode("ascii", "ignore").decode("utf-8")}')
                # Create our shortname. This will remove the base directory from the file. Eg
                # If are scanning C:\ABC\, the file C:\ABC\DEF\123.txt will be DEF\123.txt
                short_name = file.replace(directory + os.path.sep, "")
                # Setup destination name which is just joining prefix if it exists
                dest_name = os.path.join(prefix if prefix else '', short_name)
                filesize = os.stat(file).st_size
                if filename_format_func:
                    dest_name = filename_format_func(dest_name)
                # Process assets separately than regular files
                if short_name.startswith("Assets"):
                    if assets:
                        file_list.add((file, dest_name, uuid.UUID(calculate_md5(file)), filesize))
                else:
                    file_list.add((file, dest_name, uuid.UUID(calculate_md5(file)), filesize))

    # Now strip file that match exclude patterns. We do this after since the regular expressions here are a bit more expensive, so a we are at the
    # minimum possible files we must scan as this point. We did possible calculate extra md5s here
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"File count before excluding: {len(file_list)} in {directory}")
    result = set([f for f in file_list if not is_file_excluded(f[0], exclude_patterns)])
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"File count after excluding: {len(file_list)} in {directory}")
    return result


def is_file_excluded(filename: str, exclude_patterns: List[str]) -> bool:
    """
    Is file excluded by excluded patterns.

    Args:
        filename: File to filter
        exclude_patterns: List of file patterns to exclude

    Returns:
        True is file is excluded
    """
    for pattern in exclude_patterns:
        if PurePath(filename.lower()).match(pattern.lower()):
            return True
    return False


def gather_files_from_related(work_item: WorkItem, file_patterns: List[str], exclude_patterns: List[str], assets: bool, simulation_prefix_format_str: str, work_item_prefix_format_str: str, entity_filter_func: EntityFilterFunc,
                              filename_format_func: FilenameFormatFunction) -> SetOfAssets:  # pragma: no cover
    """
    Gather files from different related entities.

    Args:
        work_item: Work item to gather from
        file_patterns: List of File Patterns
        exclude_patterns: List of Exclude patterns
        assets: Should items be gathered from Assets Directory
        simulation_prefix_format_str: Format string for prefix of Simulations
        work_item_prefix_format_str: Format string for prefix of WorkItem
        entity_filter_func: Function to filter entities
        filename_format_func: Filename filter function

    Returns:
        Set of File Tuples in format Filename, Destination Name, and Checksum
    """
    file_list = set()
    # Setup threading work using a future list and a ThreadPoolExecutor
    futures = []
    pool = ThreadPoolExecutor()
    if logger.isEnabledFor(DEBUG):
        logger.debug("Filtering experiments")
    filter_experiments(assets, entity_filter_func, exclude_patterns, file_patterns, futures, pool, simulation_prefix_format_str, work_item, filename_format_func=filename_format_func)
    if logger.isEnabledFor(DEBUG):
        logger.debug("Filtering simulations")
    filter_simulations_files(assets, entity_filter_func, exclude_patterns, file_patterns, futures, pool, simulation_prefix_format_str, work_item, filename_format_func=filename_format_func)
    if logger.isEnabledFor(DEBUG):
        logger.debug("Filtering workitems")
    filter_work_items_files(assets, entity_filter_func, exclude_patterns, file_patterns, futures, pool, work_item, work_item_prefix_format_str, filename_format_func=filename_format_func)

    if logger.isEnabledFor(DEBUG):
        logger.debug("Waiting on filtering to complete")
    # Now wait until scanning items has completed
    for future in tqdm(as_completed(futures), total=len(futures), desc="Filtering relations for files"):
        file_list.update(future.result())

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Total Files found: {len(file_list)}")
    return file_list


def filter_experiments(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, work_item: WorkItem,
                       filename_format_func: FilenameFormatFunction):  # pragma: no cover
    """
    Filter Experiments outputs using our patterns.

    Args:
        assets: Assets to filter
        entity_filter_func: Function to filter functions
        exclude_patterns_compiles: List of patterns to exclude
        file_patterns: File patterns to match
        futures: Future queue
        pool: Pool to execute jobs on
        simulation_prefix_format_str: Format string for prefix of Simulations
        work_item: Parent WorkItem
        filename_format_func: Function to filter filenames

    Returns:
        None
    """
    # Start with experiments since they are the most complex portion
    experiments: List[Experiment] = work_item.get_related_experiments()
    for experiment in experiments:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Running filter on {experiment.name}/{experiment.id}')
        if entity_filter_func(experiment):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading simulations for filter on {experiment.name}/{experiment.id}')
            # Fetch simulations with the hpc_jobs criteria. This allows us to lookup the directory
            simulations = experiment.get_simulations(HPC_JOBS_QUERY)
            if logger.isEnabledFor(DEBUG):
                logger.debug(f"Total simulations to evaluate {len(simulations)}")
            if len(simulations) > 0:
                filter_experiment_assets(work_item, assets, entity_filter_func, exclude_patterns_compiles, experiment, file_patterns, futures, pool, simulation_prefix_format_str, simulations, filename_format_func=filename_format_func)
                # Loop through each simulation and queue it up for file matching
                filter_simulation_list(assets, entity_filter_func, exclude_patterns_compiles, file_patterns, futures, pool, simulation_prefix_format_str, simulations, work_item, experiment=experiment, filename_format_func=filename_format_func)


def get_simulation_prefix(parent_work_item: WorkItem, simulation: Simulation, simulation_prefix_format_str: str, experiment: Experiment = None) -> str:
    """
    Get Simulation Prefix.

    Args:
        parent_work_item: Parent workitem
        simulation: Simulation to form
        simulation_prefix_format_str: Prefix format string
        experiment: Optional experiment to be used with the

    Returns:
        Name of the simulation
    """
    prefix = simulation_prefix_format_str.format(simulation=simulation, experiment=experiment, parent_workitem=parent_work_item) if simulation_prefix_format_str else None
    if logger.isEnabledFor(DEBUG):
        logger.debug(f'Simulation Prefix: {prefix}')
    return prefix


def filter_experiment_assets(
        work_item: WorkItem, assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, experiment: Experiment, file_patterns: List[str],
        futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, simulations: List[Simulation], filename_format_func: FilenameFormatFunction):  # pragma: no cover
    """
    Filter experiment assets. This method uses the first simulation to gather experiment assets.

    Args:
        work_item: Parent Workitem
        assets: Whether assets should be matched
        entity_filter_func: Entity Filter Function
        exclude_patterns_compiles: List of files to exclude
        experiment: Experiment
        file_patterns: File patterns to filter
        futures: List of futures
        pool: Pool to submit search jobs to
        simulation_prefix_format_str: Format string for simulation
        simulations: List of simulations
        filename_format_func: Name function for filename

    Returns:
        None
    """
    # If we should gather assets, use the first simulation. It means we will duplicate some work, but the set will filter out duplicated
    if assets:
        # find the first simulation we can use to gather assets from
        i = 0
        while not entity_filter_func(simulations[i]) and i < len(simulations):
            i += 1
        if i < len(simulations):
            simulation = simulations[i]
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading assets for {experiment.name} from simulation {simulation.id}')
            # create prefix from the format var
            prefix = get_simulation_prefix(work_item, simulation, simulation_prefix_format_str, experiment)
            futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix, filename_format_func=filename_format_func))


def filter_simulations_files(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, work_item: WorkItem,
                             filename_format_func: FilenameFormatFunction):  # pragma: no cover
    """
    Filter Simulations files.

    Args:
        assets: Whether assets should be matched
        entity_filter_func: Entity Filter Function
        exclude_patterns_compiles: List of files to exclude
        file_patterns: File patterns to filter
        futures: List of futures
        pool: Pool to submit search jobs to
        simulation_prefix_format_str: Format string for simulation
        work_item:
        filename_format_func: Filename function

    Returns:
        None
    """
    # Here we loop through simulations directly added by user. We do not
    simulations: List[Simulation] = work_item.get_related_simulations()
    filter_simulation_list(assets, entity_filter_func, exclude_patterns_compiles, file_patterns, futures, pool, simulation_prefix_format_str, simulations, work_item, filename_format_func=filename_format_func)


def filter_simulation_list(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, simulations: List[Simulation], work_item: WorkItem,
                           experiment: Experiment = None, filename_format_func: FilenameFormatFunction = None):  # pragma: no cover
    """
    Filter simulations list. This method is used for experiments and simulations.

    Args:
        assets: Whether assets should be matched
        entity_filter_func: Entity Filter Function
        exclude_patterns_compiles: List of files to exclude
        file_patterns: File patterns to filter
        futures: List of futures
        pool: Pool to submit search jobs to
        simulation_prefix_format_str: Format string for simulation
        simulations: List of simulations
        work_item: Parent workitem
        experiment: Optional experiment.
        filename_format_func: Filename function

    Returns:
        None
    """
    for simulation in simulations:
        if entity_filter_func(simulation):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading outputs from Simulation {simulation.id} with status of {simulation.state}')
            prefix = get_simulation_prefix(parent_work_item=work_item, experiment=experiment, simulation=simulation, simulation_prefix_format_str=simulation_prefix_format_str)
            if simulation.hpc_jobs is None:
                simulation = simulation.get(simulation.id, HPC_JOBS_QUERY)
            futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix, filename_format_func=filename_format_func))


def filter_work_items_files(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, work_item: WorkItem, work_item_prefix_format_str: str,
                            filename_format_func: FilenameFormatFunction):  # pragma: no cover
    """
    Filter work items files.

    Args:
        assets: Whether assets should be matched
        entity_filter_func: Entity Filter Function
        exclude_patterns_compiles: List of files to exclude
        file_patterns: File patterns to filter
        futures: List of futures
        pool: Pool to submit search jobs to
        work_item: WorkItem
        work_item_prefix_format_str: WorkItemPrefix
        filename_format_func: Filename function

    Returns:
        None
    """
    # Here we loop through workitems
    work_items: List[WorkItem] = work_item.get_related_work_items()
    for related_work_item in work_items:
        if entity_filter_func(related_work_item):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading outputs from WorkItem {related_work_item.name} - {related_work_item.id}')
            prefix = work_item_prefix_format_str.format(work_item=related_work_item, parent_work_item=work_item) if work_item_prefix_format_str else None
            futures.append(pool.submit(gather_files, directory=related_work_item.working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix, filename_format_func=filename_format_func))


def filter_ac_files(wi: WorkItem, patterns, exclude_patterns) -> List[AssetCollectionFile]:  # pragma: no cover
    """
    Filter Asset Collection File.

    Args:
        wi: WorkItem
        patterns: File patterns
        exclude_patterns: Exclude patterns

    Returns:
        List of filters asset collection files
    """
    if logger.isEnabledFor(DEBUG):
        logger.debug('Filtering asset collections')
    relates_acs: List[AssetCollection] = wi.get_related_asset_collections(relation_type=RelationType.DependsOn)
    filtered_ac_files = set()
    for ac in relates_acs:
        ac = ac.get(ac.id, QueryCriteria().select_children("assets"))
        for file in ac.assets:
            file_path = get_asset_file_path(file)
            for pattern in patterns:
                if PurePath(file_path).match(pattern):
                    filtered_ac_files.add(file)
                    # break out of pattern loop since there was a match
                    break

    return [f for f in filtered_ac_files if not is_file_excluded(get_asset_file_path(f), exclude_patterns)]


def get_asset_file_path(file):
    """
    Get asset file path which combined the relative path and filename if relative path is set.

    Otherwise we use just the filename.

    Args:
        file: Filename

    Returns:
        Filename
    """
    return os.path.join(file.relative_path, file.file_name) if file.relative_path else file.file_name


class DuplicateAsset(Exception):
    """Error for when we encountered output paths that overlap."""
    doc_link: str = "platforms/comps/assetize_output.html#errors"


def ensure_no_duplicates(ac_files, files):  # pragma: no cover
    """
    Ensure no duplicates are in asset.

    Args:
        ac_files: Ac files
        files: Simulation/Experiment/Workitem files

    Returns:
        None

    Raises:
        DuplicateAsset - if asset with same output path is found
    """
    dest_paths = defaultdict(int)
    for file in ac_files:
        fn = os.path.join(file.relative_path, file.file_name) if file.relative_path else file.file_name
        dest_paths[fn] += 1
    for file in files:
        dest_paths[file[1]] += 1
    # we should have one count for all items(1). If we have more than one count, than there are duplicates
    if any([x > 1 for x in set(dest_paths.values())]):
        duplicate_assets = [x for x, count in dest_paths.items() if count > 1]
        error_files = []
        # match up to assets
        for asset in ac_files:
            fn = os.path.join(asset.relative_path, asset.file_name) if asset.relative_path else asset.file_name
            if fn in duplicate_assets:
                error_files.append(f'{fn} from Asset Collections')
        for file in files:
            if file[1] in duplicate_assets:
                error_files.append(f'{file[1]}<{file[0]}> from Experiment, Simulation, or WorkItem')
        nl = "\n"
        raise DuplicateAsset(f"The following assets have duplicate destination paths:{nl} {nl.join(sorted(error_files))}")


def print_results(ac_files, files):  # pragma: no cover
    """
    Print Results.

    Args:
        ac_files: Ac Files
        files: Files

    Returns:
        None
    """
    all_files = []
    for file in files:
        all_files.append(dict(filename=file[0], destname=file[1], filesize=file[3]))
    total_file_size = sum([f[3] for f in files])
    for af in ac_files:
        fn = get_asset_file_path(af)
        all_files.append(dict(filename=fn, destname=fn, filesize=af._length))
    with open("file_list.json", 'w') as flist:
        json.dump(all_files, flist, indent=4, sort_keys=True)
    header = all_files[0].keys()
    rows = [x.values() for x in sorted(all_files, key=lambda x: x['destname'])]
    with open("file_list.html", "w") as html_list:
        html_list.write(tabulate(rows, header, tablefmt='html'))

    print(f'Total asset collection size: {humanfriendly.format_size(total_file_size)}')


def apply_custom_filters(args: argparse.Namespace):
    """
    Apply user defined custom filter functions.

    The function does the following workflow.

    1. Check if there is a pre_run_func(s) defined.
    1b) If there are pre-run funcs, run each of those
    2) Is there an entity_filter_func. This function allows us to filter items(Experiment/Simulations/etc) directly. If not defined, we use a default function returns true.
    3) If filename format function is defined, we set that, otherwise we use the default which just uses the original file name

    Args:
        args: argparse namespace.

    Returns:
        entity_filter_func and filename format func
    """
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
        if logger.isEnabledFor(DEBUG):
            logger.debug("Setting default filter function")

        def default_filter_func(x):
            return True

        entity_filter_func = default_filter_func

    if args.filename_format_func:
        import filename_format_func
        fn_format_func = getattr(filename_format_func, args.filename_format_func)
    else:
        def default_format_func(s: str):
            return s

        fn_format_func = default_format_func

    return entity_filter_func, fn_format_func


def parse_filter_args_common(args: argparse.Namespace):
    """
    Parse filter arguments from an argparse namespace.

    We need this because we use filtering across multiple scripts.

    Args:
        args: Argparse args

    Returns:
        entity_filter_func and filename formart func
    """
    if args.verbose:
        setup_verbose(args)
    if "**" in args.file_pattern:
        args.file_pattern = ["**"]
    entity_filter_func, fn_format_func = apply_custom_filters(args)
    for i, a in enumerate(args.exclude_pattern):
        args.exclude_pattern[i] = a.replace("\\*", "*")
    for i, a in enumerate(args.file_pattern):
        if a.startswith("'") and a.endswith("'"):
            args.file_pattern[i] = a.replace("\\*", "*")
    for i in ['simulation_prefix_format_str', 'work_item_prefix_format_str']:
        si = getattr(args, i)
        if si and si.startswith("'") and si.endswith("'"):
            si = si.strip("'")
            setattr(args, i, si)
    return entity_filter_func, fn_format_func


def filter_files_and_assets(args: argparse.Namespace, entity_filter_func: EntityFilterFunc, wi: WorkItem, filename_format_func: FilenameFormatFunction) -> Tuple[SetOfAssets, List[AssetCollectionFile]]:
    """
    Filter files and assets using provided parameters.

    Args:
        args: Argparse details
        entity_filter_func: Optional filter function for entities. This function is ran on every item. If it returns true, we return the item
        wi: WorkItem we are running in
        filename_format_func: Filename format function allows use to customize how we filter filenames for output.

    Returns:
        Files that matches the filter and the assets that matches the filter as well.
    """
    files = gather_files_from_related(
        wi, file_patterns=args.file_pattern, exclude_patterns=args.exclude_pattern if args.exclude_pattern else [], assets=args.assets,
        work_item_prefix_format_str=args.work_item_prefix_format_str,
        simulation_prefix_format_str=args.simulation_prefix_format_str if not args.no_simulation_prefix else None,
        entity_filter_func=entity_filter_func, filename_format_func=filename_format_func
    )
    files_from_ac: List[AssetCollectionFile] = filter_ac_files(wi, args.file_pattern, args.exclude_pattern)
    return files, files_from_ac
