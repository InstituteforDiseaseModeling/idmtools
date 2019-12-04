from COMPS.Data.Simulation import SimulationState
from requests import RequestException

from idmtools.core import EntityStatus


def convert_COMPS_status(comps_status: SimulationState) -> EntityStatus:
    """
    Converts comps status object to common EntityStatus

    Args:
        comps_status: Comps status

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
