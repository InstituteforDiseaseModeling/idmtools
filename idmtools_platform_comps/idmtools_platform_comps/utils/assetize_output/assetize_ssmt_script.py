import glob
import json
from collections import defaultdict
from pathlib import PurePath
import traceback
import sys
from logging import getLogger, DEBUG
import humanfriendly
from COMPS.Data.Simulation import SimulationState
from COMPS.Data.WorkItem import WorkItemState, RelationType
from concurrent.futures._base import as_completed, Future
from concurrent.futures.thread import ThreadPoolExecutor
import uuid
from tabulate import tabulate
from tqdm import tqdm
from typing import List, Tuple, Set, Dict, Callable
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
# Store the Done State
DONE_STATE = [SimulationState.Failed, SimulationState.Canceled, SimulationState.Succeeded]
HPC_JOBS_QUERY = QueryCriteria().select_children('hpc_jobs')

JOB_CONFIG = None


class NoFileFound(Exception):
    doc_link: str = "platforms/comps/assetize_output.html#errors"


class DuplicateAsset(Exception):
    doc_link: str = "platforms/comps/assetize_output.html#errors"


def gather_files(directory: str, file_patterns: List[str], exclude_patterns: List[str] = None, assets: bool = False, prefix: str = None) -> SetOfAssets:
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

        sd = os.path.join(directory, pattern)
        if logger.isEnabledFor(DEBUG):
            logger.debug(f'Looking for files with pattern {sd}')
        for file in glob.iglob(sd, recursive=True):
            # Ensure it is a file and not a directory
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'{file} matching pattern. Is Dir: {os.path.isdir(file)}. Is Link: {os.path.islink(file)}')
            if os.path.isfile(file):
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f'Found file {file}')
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
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"File count before excluding: {len(file_list)} in {directory}")
    result = set([f for f in file_list if not is_file_excluded(f[0], exclude_patterns)])
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"File count after excluding: {len(file_list)} in {directory}")
    return result


def is_file_excluded(filename: str, exclude_patterns: List[str]) -> bool:
    """

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


def gather_files_from_related(work_item: WorkItem, file_patterns: List[str], exclude_patterns: List[str], assets: bool, simulation_prefix_format_str: str, work_item_prefix_format_str: str, entity_filter_func: EntityFilterFunc) -> SetOfAssets:  # pragma: no cover
    """
    Gather files from different related entities

    Args:
        work_item: Work item to gather from
        file_patterns: List of File Patterns
        exclude_patterns: List of Exclude patterns
        assets: Should items be gathered from Assets Directory
        simulation_prefix_format_str: Format string for prefix of Simulations
        work_item_prefix_format_str: Format string for prefix of WorkItem

    Returns:
        Set of File Tuples in format Filename, Destination Name, and Checksum
    """
    file_list = set()
    # Setup threading work using a future list and a ThreadPoolExecutor
    futures = []
    pool = ThreadPoolExecutor()
    if logger.isEnabledFor(DEBUG):
        logger.debug("Filtering experiments")
    filter_experiments(assets, entity_filter_func, exclude_patterns, file_patterns, futures, pool, simulation_prefix_format_str, work_item)
    if logger.isEnabledFor(DEBUG):
        logger.debug("Filtering simulations")
    filter_simulations_files(assets, entity_filter_func, exclude_patterns, file_patterns, futures, pool, simulation_prefix_format_str, work_item)
    if logger.isEnabledFor(DEBUG):
        logger.debug("Filtering workitems")
    filter_work_items_files(assets, entity_filter_func, exclude_patterns, file_patterns, futures, pool, work_item, work_item_prefix_format_str)

    if logger.isEnabledFor(DEBUG):
        logger.debug("Waiting on filtering to complete")
    # Now wait until scanning items has completed
    for future in tqdm(as_completed(futures), total=len(futures), desc="Filtering relations for files"):
        file_list.update(future.result())

    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Total Files found: {len(file_list)}")
    return file_list


def filter_experiments(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, work_item: WorkItem):  # pragma: no cover
    """
    Filter Experiments outputs using our patterns

    Args:
        assets: Assets to filter
        entity_filter_func: Function to filter functions
        exclude_patterns_compiles: List of patterns to exclude
        file_patterns: File patterns to match
        futures: Future queue
        pool: Pool to execute jobs on
        simulation_prefix_format_str: Format string for prefix of Simulations
        work_item: Parent WorkItem

    Returns:

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
            if len(simulations) > 0:
                filter_experiment_assets(work_item, assets, entity_filter_func, exclude_patterns_compiles, experiment, file_patterns, futures, pool, simulation_prefix_format_str, simulations)
                # Loop through each simulation and queue it up for file matching
                filter_simulation_list(assets, entity_filter_func, exclude_patterns_compiles, file_patterns, futures, pool, simulation_prefix_format_str, simulations, work_item, experiment=experiment)


def get_simulation_prefix(parent_workitem: WorkItem, simulation: Simulation, simulation_prefix_format_str: str, experiment: Experiment = None) -> str:
    """
    Get Simulation Prefix

    Args:
        parent_workitem: Parent workitem
        simulation: Simulation to form
        simulation_prefix_format_str: Prefix format string
        experiment: Optional experiment to be used with the

    Returns:
        Name of the simulation
    """
    prefix = simulation_prefix_format_str.format(simulation=simulation, experiment=experiment, parent_workitem=parent_workitem) if simulation_prefix_format_str else None
    return prefix


def filter_experiment_assets(work_item: WorkItem, assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, experiment: Experiment, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, simulations: List[Simulation]):  # pragma: no cover
    """
    Filter experiment assets. This method uses the first simulation to gather experiment assets

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

    Returns:

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
            futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix))


def filter_simulations_files(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, work_item: WorkItem):  # pragma: no cover
    """
    Filter Simulations files

    Args:
        assets: Whether assets should be matched
        entity_filter_func: Entity Filter Function
        exclude_patterns_compiles: List of files to exclude
        file_patterns: File patterns to filter
        futures: List of futures
        pool: Pool to submit search jobs to
        simulation_prefix_format_str: Format string for simulation
        work_item:

    Returns:

    """
    # Here we loop through simulations directly added by user. We do not
    simulations: List[Simulation] = work_item.get_related_simulations()
    filter_simulation_list(assets, entity_filter_func, exclude_patterns_compiles, file_patterns, futures, pool, simulation_prefix_format_str, simulations, work_item)


def filter_simulation_list(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, simulation_prefix_format_str: str, simulations: List[Simulation], work_item: WorkItem,
                           experiment: Experiment = None):  # pragma: no cover
    """
    Filter simulations list. This method is used for experiments and simulations
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

    Returns:

    """
    for simulation in simulations:
        if entity_filter_func(simulation):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading outputs from Simulation {simulation.id} with status of {simulation.state}')
            prefix = get_simulation_prefix(parent_workitem=work_item, experiment=experiment, simulation=simulation, simulation_prefix_format_str=simulation_prefix_format_str)
            if simulation.hpc_jobs is None:
                simulation = simulation.get(simulation.id, HPC_JOBS_QUERY)
            futures.append(pool.submit(gather_files, directory=simulation.hpc_jobs[0].working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix))


def filter_work_items_files(assets: bool, entity_filter_func: EntityFilterFunc, exclude_patterns_compiles: List, file_patterns: List[str], futures: List[Future], pool: ThreadPoolExecutor, work_item: WorkItem, work_item_prefix_format_str: str):  # pragma: no cover
    """
    Filter work items files

    Args:
        assets: Whether assets should be matched
        entity_filter_func: Entity Filter Function
        exclude_patterns_compiles: List of files to exclude
        file_patterns: File patterns to filter
        futures: List of futures
        pool: Pool to submit search jobs to
        work_item: WorkItem
        work_item_prefix_format_str: WorkItemPrefix

    Returns:

    """
    # Here we loop through workitems
    work_items: List[WorkItem] = work_item.get_related_work_items()
    for related_work_item in work_items:
        if entity_filter_func(related_work_item):
            if logger.isEnabledFor(DEBUG):
                logger.debug(f'Loading outputs from WorkItem {related_work_item.name} - {related_work_item.id}')
            prefix = work_item_prefix_format_str.format(work_item=related_work_item, parent_work_item=work_item) if work_item_prefix_format_str else None
            futures.append(pool.submit(gather_files, directory=related_work_item.working_directory, file_patterns=file_patterns, exclude_patterns=exclude_patterns_compiles, assets=assets, prefix=prefix))


def create_asset_collection(file_list: SetOfAssets, ac_files: List[AssetCollectionFile], asset_tags: Dict[str, str]):  # pragma: no cover
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
        asset_collection_map[file[2]] = (acf, file[0], file[3])
        asset_collection.add_asset(acf)

    # add files from acs
    for ac in ac_files:
        asset_collection.add_asset(ac)

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
                total_to_upload += asset_details[2]
                acf = AssetCollectionFile(file_name=asset_details[0].file_name, relative_path=asset_details[0].relative_path)
                ac2.add_asset(acf, asset_details[1])
            else:
                ac2.add_asset(asset_details[0])
        user_logger.info(f"Saving {new_files} totaling {humanfriendly.format_size(total_to_upload)} assets to comps")
        asset_collection.set_tags(asset_tags)
        ac2.save()
        asset_collection = ac2
    return asset_collection


def ensure_items_are_ready(work_item: WorkItem):  # pragma: no cover
    """
    Ensure items are done. This leverages COMPS sleeping to pause creation of Asset Collections until item is in a done state
    Args:
        work_item:

    Returns:

    """
    experiments: List[Experiment] = work_item.get_related_experiments()
    for experiment in experiments:
        simulations: List[Simulation] = experiment.get_simulations()
        for simulation in simulations:
            logger.debug(f'Loading outputs from Simulation {simulation.id} with status of {simulation.state}')
            if simulation.state not in DONE_STATE:
                user_logger.info(f"Pausing work until {simulation.id} is done")
                sys.exit(206)
    work_items: List[WorkItem] = work_item.get_related_work_items()

    for simulation in work_item.get_related_simulations():
        if simulation.state not in DONE_STATE:
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
    parser.add_argument("--pre-run-func", default=None, action='append', help="List of function to run before starting analysis. Useful to load packages up in docker container before run")
    parser.add_argument("--entity-filter-func", default=None, help="Name of function that can be used to filter items")
    parser.add_argument("--dry-run", default=False, action="store_true", help="Find files, but don't add")

    return parser


def assetize_error_handler(exctype, value: Exception, tb):  # pragma: no cover
    """
    Global exception handler. This will write our errors in a nice format

    Args:
        exctype: Type of exception
        value: Value of the exception
        traceback: Traceback

    Returns:
        None
    """
    if exctype is NoFileFound:
        from idmtools.utils.info import get_help_version_url
        print(f"No files were found. Check your patterns match the data from related item. For more details, see {get_help_version_url(value.doc_link)}")
    with open("error_reason.json", 'w') as err_out:
        output_error = dict(type=exctype.__name__, args=list(value.args), tb=traceback.format_tb(tb), job_config=JOB_CONFIG)
        output_error['tb'] = [t.strip() for t in output_error['tb']]
        if hasattr(value, 'doc_link'):
            output_error['doc_link'] = value.doc_link
        json.dump(output_error, err_out, indent=4, sort_keys=True)

    # Call native exception manager
    sys.__excepthook__(exctype, value, tb)


def filter_ac_files(patterns, exclude_patterns) -> List[AssetCollectionFile]:  # pragma: no cover
    """
    Filter Asset Collection File

    Args:
        patterns: File patterns
        exclude_patterns: Exclude patterns

    Returns:

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
    return os.path.join(file.relative_path, file.file_name) if file.relative_path else file.file_name


def print_results(ac_files, files):  # pragma: no cover
    """
    Print Results

    Args:
        ac_files: Ac Files
        files: Files

    Returns:

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


def ensure_no_duplicates(ac_files, files):  # pragma: no cover
    """
    Ensure no duplicates are in asset
    Args:
        ac_files: Ac files
        files: Simulation/Experiment/Workitem files

    Returns:

    """
    dest_paths = defaultdict(int)
    for file in ac_files:
        fn = os.path.join(file.relative_path, file.file_name) if file.relative_path else file.file_name
        dest_paths[fn] += 1
    for file in files:
        dest_paths[file[1]] += 1
    # we should have one count for all items(1). If we have more than one count, than there are duplicates
    if len(set(dest_paths.keys())) > 1:
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


if __name__ == "__main__":  # pragma: no cover
    parser = get_argument_parser()
    args = parser.parse_args()

    JOB_CONFIG = vars(args)

    if args.verbose:
        # set to debug before loading idmtools
        os.environ['IDMTOOLS_LOGGING_LEVEL'] = 'DEBUG'
        os.environ['IDMTOOLS_LOGGING_CONSOLE'] = 'on'
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
        if logger.isEnabledFor(DEBUG):
            logger.debug("Setting default filter function")

        def default_filter_func(x):
            return True

        entity_filter_func = default_filter_func

    # load the work item
    client = Client()
    client.login(os.environ['COMPS_SERVER'])
    wi = WorkItem.get(os.environ['COMPS_WORKITEM_GUID'])
    asset_tags = dict()
    if args.asset_tag:
        for tag in args.asset_tag:
            name, value = tag.split("=")
            asset_tags[name] = value
    # register our error handler
    sys.excepthook = assetize_error_handler
    # Run a check that all our dependencies have been loaded
    ensure_items_are_ready(wi)
    if "**" in args.file_pattern:
        args.file_pattern = ["**"]
    # Gather all our files
    files = gather_files_from_related(
        wi, file_patterns=args.file_pattern, exclude_patterns=args.exclude_pattern if args.exclude_pattern else [], assets=args.assets,
        work_item_prefix_format_str=args.work_item_prefix_format_str,
        simulation_prefix_format_str=args.simulation_prefix_format_str if not args.no_simulation_prefix else None,
        entity_filter_func=entity_filter_func
    )

    ac_files: List[AssetCollectionFile] = filter_ac_files(args.file_pattern, args.exclude_pattern)
    if len(files) == 0 and len(ac_files) == 0:
        raise NoFileFound("No files found for related items")

    ensure_no_duplicates(ac_files, files)

    if args.dry_run:
        print_results(ac_files, files)
    else:
        ac = create_asset_collection(files, ac_files, asset_tags=asset_tags)

        with open('asset_collection.id', 'w') as o:
            user_logger.info(ac.id)
            o.write(str(ac.id))

        wi.add_related_asset_collection(ac.id, RelationType.Created)
