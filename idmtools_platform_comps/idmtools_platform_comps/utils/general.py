import ntpath
from typing import List, Dict
from uuid import UUID

from COMPS.Data import Simulation
from COMPS.Data.Simulation import SimulationState
from COMPS.Data.WorkItem import WorkItemState
from idmtools.core import EntityStatus, ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.iplatform import IPlatform
from requests import RequestException


def fatal_code(e: Exception) -> bool:
    """
    Uses to determine if we should stop retrying based on request status code

    Args:
        e: Exeception to check

    Returns:
        True is exception is a request and status code matches 404
    """
    if isinstance(e, RequestException):
        return 404 == e.response.status_code
    return False


def convert_comps_status(comps_status: SimulationState) -> EntityStatus:
    """
    Convert status from COMPS to IDMTools

    Args:
        comps_status: Status in Comps

    Returns:
        EntityStatus
    """
    if comps_status == SimulationState.Succeeded:
        return EntityStatus.SUCCEEDED
    elif comps_status in (SimulationState.Canceled, SimulationState.CancelRequested, SimulationState.Failed):
        return EntityStatus.FAILED
    elif comps_status == SimulationState.Created:
        return EntityStatus.CREATED
    else:
        return EntityStatus.RUNNING


def convert_comps_workitem_status(comps_status: WorkItemState) -> EntityStatus:
    """
    Convert status from COMPS to IDMTools
    Created = 0                # WorkItem has been saved to the database
    CommissionRequested = 5    # WorkItem is ready to be processed by the next available worker of the correct type
    Commissioned = 10          # WorkItem has been commissioned to a worker of the correct type and is beginning execution
    Validating = 30            # WorkItem is being validated
    Running = 40               # WorkItem is currently running
    Waiting = 50               # WorkItem is waiting for dependent items to complete
    ResumeRequested = 60       # Dependent items have completed and WorkItem is ready to be processed by the next available worker of the correct type
    CancelRequested = 80       # WorkItem cancellation was requested
    Canceled = 90              # WorkItem was successfully canceled
    Resumed = 100              # WorkItem has been claimed by a worker of the correct type and is resuming
    Canceling = 120            # WorkItem is in the process of being canceled by the worker
    Succeeded = 130            # WorkItem completed successfully
    Failed = 140               # WorkItem failed
    Args:
        comps_status: Status in Comps

    Returns:
        EntityStatus
    """
    if comps_status == WorkItemState.Succeeded:
        return EntityStatus.SUCCEEDED
    elif comps_status in (WorkItemState.Canceled, WorkItemState.CancelRequested, WorkItemState.Failed):
        return EntityStatus.FAILED
    elif comps_status == [WorkItemState.Created, WorkItemState.Resumed, WorkItemState.CommissionRequested, WorkItemState.Commissioned]:
        return EntityStatus.CREATED
    else:
        return EntityStatus.RUNNING


def clean_experiment_name(experiment_name: str) -> str:
    """
    Enforce any COMPS-specific demands on experiment names.
    Args:
        experiment_name: name of the experiment
    Returns:the experiment name allowed for use
    """
    for c in ['/', '\\', ':']:
        experiment_name = experiment_name.replace(c, '_')
    return experiment_name


def get_file_from_collection(platform: IPlatform, collection_id: UUID, file_path: str) -> bytearray:
    """
    Retrieve a file from an asset collection

    Args:
        platform: Platform object to use
        collection_id: Asset Collection ID
        file_path: Path within collection

    Returns:
        Object Byte Array
    """
    print(f"Cache miss for {collection_id} {file_path}")

    # retrieve the collection
    ac = platform.get_item(collection_id, ItemType.ASSETCOLLECTION, raw=True)

    # Look for the asset file in the collection
    file_name = ntpath.basename(file_path)
    path = ntpath.dirname(file_path).lstrip(f"Assets\\")

    for asset_file in ac.assets:
        if asset_file.file_name == file_name and (asset_file.relative_path or '') == path:
            return asset_file.retrieve()


def get_asset_for_comps_item(platform: IPlatform, item: IEntity, files: List[str], cache=None) -> Dict[str, bytearray]:
    """
    Retrieve assets from an Entity(Simulation, Experiment, WorkItem)

    Args:
        platform: Platform Object to use
        item: Item to fetch assets from
        files: List of file names to retrieve
        cache: Cache object to use

    Returns:
        Dictionary in structure of filename -> bytearray
    """
    # Retrieve comps item
    if item.platform is None:
        item.platform = platform
    comps_item: Simulation = item.get_platform_object(True, children=["files", "configuration"])

    all_paths = set(files)
    assets = set(path for path in all_paths if path.lower().startswith("assets"))
    transients = all_paths.difference(assets)

    # Create the return dict
    ret = {}

    # Retrieve the transient if any
    if transients:
        transient_files = comps_item.retrieve_output_files(paths=transients)
        ret = dict(zip(transients, transient_files))

    # Take care of the assets
    if assets and comps_item.configuration:
        # Get the collection_id for the simulation
        collection_id = comps_item.configuration.asset_collection_id
        # Retrieve the files
        for file_path in assets:
            # Normalize the separators
            normalized_path = ntpath.normpath(file_path)
            if cache is not None:
                ret[file_path] = cache.memoize()(get_file_from_collection)(platform, collection_id, normalized_path)
            else:
                ret[file_path] = get_file_from_collection(platform, collection_id, normalized_path)
    return ret
