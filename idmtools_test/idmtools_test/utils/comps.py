from COMPS import Data
from COMPS.Data import QueryCriteria, Simulation as COMPSSimulation, Simulation


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


def sims_from_experiment(e):
    return e.get_simulations(QueryCriteria().select(['id', 'state']).select_children('hpc_jobs'))


def workdirs_from_simulations(sims):
    return {str(sim.id): sim.hpc_jobs[-1].working_directory for sim in sims if sim.hpc_jobs}


def get_simulation_path(simulation):
    path = workdirs_from_simulations([simulation])[str(simulation.id)]
    return path


def get_simulation_by_id(sim_id, query_criteria=None):
    return Simulation.get(id=sim_id, query_criteria=query_criteria)
