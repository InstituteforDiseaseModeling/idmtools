from COMPS.Data.Simulation import SimulationState
from idmtools.core.enums import EntityStatus


def convert_COMPS_status(comps_status):
    if comps_status == SimulationState.Succeeded:
        return EntityStatus.SUCCEEDED
    elif comps_status in (SimulationState.Canceled, SimulationState.CancelRequested, SimulationState.Failed):
        return EntityStatus.FAILED
    elif comps_status == SimulationState.Created:
        return EntityStatus.CREATED
    else:
        return EntityStatus.RUNNING
