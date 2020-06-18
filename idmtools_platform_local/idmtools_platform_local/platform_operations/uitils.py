from logging import getLogger, DEBUG
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from idmtools.core import EntityStatus

logger = getLogger(__name__)

status_translate = dict(
    created='CREATED',
    in_progress='RUNNING',
    canceled='FAILED',
    failed='FAILED',
    done='SUCCEEDED'
)


class ExperimentDict(dict):
    pass


class SimulationDict(dict):
    pass


def local_status_to_common(status) -> 'EntityStatus':
    """
    Convert local platform status to idmtools status
    Args:
        status:

    Returns:

    """
    from idmtools.core import EntityStatus
    return EntityStatus[status_translate[status]]


def download_lp_file(filename: str, buffer_size: int = 128) -> Generator[bytes, None, None]:
    """
    Returns a generator to download files on the local platform
    Args:
        filename:
        buffer_size:

    Returns:

    """
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Streaming file {filename}")
    with open(filename, 'rb') as out:
        while True:
            chunk = out.read(buffer_size)
            if chunk:
                yield chunk
            else:
                if logger.isEnabledFor(DEBUG):
                    logger.debug(f"Finished streaming file {filename}")
                break
