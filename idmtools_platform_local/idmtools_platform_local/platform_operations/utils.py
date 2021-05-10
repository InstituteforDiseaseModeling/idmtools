"""idmtools local platform operations utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from logging import getLogger, DEBUG
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:  # pragma: no cover
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
    """Alias for local platform experiment objects."""
    pass


class SimulationDict(dict):
    """Alias for local platform simulation objects."""
    pass


def local_status_to_common(status) -> 'EntityStatus':
    """
    Convert local platform status to idmtools status.

    Args:
        status:

    Returns:
        Local platform status
    """
    from idmtools.core import EntityStatus
    return EntityStatus[status_translate[status]]


def download_lp_file(filename: str, buffer_size: int = 128) -> Generator[bytes, None, None]:
    """
    Returns a generator to download files on the local platform.

    Args:
        filename: Filename to download
        buffer_size: Buffer size

    Returns:
        Generator for file content
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
