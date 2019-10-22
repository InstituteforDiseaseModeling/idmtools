from COMPS import Data
from COMPS.Data import QueryCriteria, Simulation as COMPSSimulation


def get_asset_collection_id_for_simulation_id(sim_id):
    simulation = COMPSSimulation.get(sim_id, query_criteria=QueryCriteria().select(
        ['id', 'experiment_id']).select_children(
        ["files", "configuration"]))

    collection_id = simulation.configuration.asset_collection_id
    return collection_id


def get_asset_collection_by_id(collection_id, query_criteria=None):
    query_criteria = query_criteria or QueryCriteria().select_children('assets')
    try:
        return Data.AssetCollection.get(collection_id, query_criteria)
    except (RuntimeError, ValueError):
        return None
