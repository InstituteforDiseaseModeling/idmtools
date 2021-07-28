import ntpath
import re
from logging import getLogger, DEBUG
from typing import List, Dict, Union, Generator, Optional
from uuid import UUID

from COMPS import Client
from COMPS.Data import Simulation, SimulationFile, AssetCollectionFile, WorkItemFile, OutputFileMetadata, Experiment
from COMPS.Data.AssetFile import AssetFile
from COMPS.Data.Simulation import SimulationState
from COMPS.Data.WorkItem import WorkItemState, WorkItem
from requests import RequestException

from idmtools.core import EntityStatus, ItemType
from idmtools.core.interfaces.ientity import IEntity
from idmtools.entities.iplatform import IPlatform

ASSETS_PATH = "Assets\\"

logger = getLogger(__name__)

chars_to_replace = ['/', '\\', ':', "'", '"', '?', '<', '>', '*', '|', "\0", "(", ")", '`']
clean_names_expr = re.compile(f'[{re.escape("".join(chars_to_replace))}]')


def fatal_code(e: Exception) -> bool:
    """
    Uses to determine if we should stop retrying based on request status code

    Args:
        e: Exeception to check

    Returns:
        True is exception is a request and status code matches 404
    """
    if isinstance(e, RequestException):
        return e.response.status_code == 404
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
    work_item_canceled = (WorkItemState.Canceled, WorkItemState.CancelRequested, WorkItemState.Failed)
    work_item_created = [
        WorkItemState.Created, WorkItemState.Resumed, WorkItemState.CommissionRequested, WorkItemState.Commissioned
    ]
    if comps_status == WorkItemState.Succeeded:
        return EntityStatus.SUCCEEDED
    elif comps_status in work_item_canceled:
        return EntityStatus.FAILED
    elif comps_status == work_item_created:
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

    experiment_name = clean_names_expr.sub("_", experiment_name)
    return experiment_name.encode("ascii", "ignore").decode('utf8').strip()


def get_file_from_collection(platform: IPlatform, collection_id: UUID, file_path: str) -> bytearray:
    """
    Retrieve a file from an asset collection

    Args:
        platform: Platform object to use
        collection_id: Asset Collection ID
        file_path: Path within collection

    Examples::
    >>> import uuid
    >>> get_file_from_collection(platform, uuid.UUID("fc461146-3b2a-441f-bc51-0bff3a9c1ba0"), "StdOut.txt")

    Returns:
        Object Byte Array
    """
    print(f"Cache miss for {collection_id} {file_path}")

    # retrieve the collection
    ac = platform.get_item(collection_id, ItemType.ASSETCOLLECTION, raw=True)

    # Look for the asset file in the collection
    file_name = ntpath.basename(file_path)
    path = ntpath.dirname(file_path).lstrip(ASSETS_PATH)

    for asset_file in ac.assets:
        if asset_file.file_name == file_name and (asset_file.relative_path or '') == path:
            return asset_file.retrieve()


def get_file_as_generator(file: Union[SimulationFile, AssetCollectionFile, AssetFile, WorkItemFile, OutputFileMetadata],
                          chunk_size: int = 128, resume_byte_pos: Optional[int] = None) -> \
        Generator[bytearray, None, None]:
    """
    Get file as a generator

    Args:
        file: File to stream contents through a generator
        chunk_size: Size of chunks to load
        resume_byte_pos: Optional start of download

    Returns:

    """
    if isinstance(file, OutputFileMetadata):
        url = file.url
    else:
        url = file.uri
    i = url.find('/asset/')
    if i == -1:
        raise RuntimeError('Unable to parse asset url: ' + url)

    if resume_byte_pos:
        header = {'Range': 'bytes=%d-' % resume_byte_pos}
    else:
        header = {}
    response = Client.get(url[i:], headers=header, stream=True)

    yield from response.iter_content(chunk_size=chunk_size)


class Workitem(object):
    pass


def get_asset_for_comps_item(platform: IPlatform, item: IEntity, files: List[str], cache=None, load_children: List[str] = None, comps_item: Union[Experiment, Workitem, Simulation] = None) -> Dict[str, bytearray]:
    """
    Retrieve assets from an Entity(Simulation, Experiment, WorkItem)

    Args:
        platform: Platform Object to use
        item: Item to fetch assets from
        files: List of file names to retrieve
        cache: Cache object to use
        load_children: Optional Load children fields
        comps_item: Optional comps item

    Returns:
        Dictionary in structure of filename -> bytearray
    """
    # Retrieve comps item
    if load_children is None:
        load_children = ["files", "configuration"]
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Loading the files {files} from {item}")
    if item.platform is None:
        item.platform = platform
    if comps_item is None:
        comps_item = item.get_platform_object(True, load_children=load_children)

    if len(files) == 0:
        transients = []
        assets = None
    else:
        all_paths = set(files)
        assets = set(path for path in all_paths if path.lower().startswith("assets"))
        transients = all_paths.difference(assets)

    # Create the return dict
    ret = {}

    # Retrieve the transient if any
    if isinstance(comps_item, (Simulation, WorkItem)):
        if transients or len(files) == 0:
            transient_files = comps_item.retrieve_output_files(paths=transients)
            ret = dict(zip(transients, transient_files))
    else:
        ret = dict()

    # Take care of the assets
    if assets and comps_item.configuration:
        # Get the collection_id for the simulation
        collection_id = comps_item.configuration.asset_collection_id
        if collection_id:
            # Retrieve the files
            for file_path in assets:
                # Normalize the separators
                normalized_path = ntpath.normpath(file_path)
                if cache is not None:
                    ret[file_path] = cache.memoize()(get_file_from_collection)(platform, collection_id, normalized_path)
                else:
                    ret[file_path] = get_file_from_collection(platform, collection_id, normalized_path)
    return ret
