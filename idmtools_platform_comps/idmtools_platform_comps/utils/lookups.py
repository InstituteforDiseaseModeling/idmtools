"""idmtools comps lookups.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from datetime import datetime, timedelta
from logging import getLogger
from typing import List
import backoff
from COMPS.Data import Experiment, Simulation, QueryCriteria
from requests import Timeout, HTTPError
from idmtools_platform_comps.utils.general import fatal_code

logger = getLogger(__name__)


@backoff.on_exception(backoff.constant(1.5), (Timeout, ConnectionError, HTTPError), max_tries=5, giveup=fatal_code)
def get_experiment_by_id(exp_id, query_criteria: QueryCriteria = None) -> Experiment:
    """Get an experiment by id."""
    return Experiment.get(exp_id, query_criteria=query_criteria)


@backoff.on_exception(backoff.constant(1.5), (Timeout, ConnectionError, HTTPError), max_tries=5, giveup=fatal_code)
def get_simulation_by_id(sim_id, query_criteria: QueryCriteria = None) -> Simulation:
    """
    Fetches simulation by id and optional query criteria.

    Wrapped in additional Retry Logic. Used by other lookup methods

    Args:
        sim_id:
        query_criteria: Optional QueryCriteria to search with

    Returns:
        Simulation with ID
    """
    return Simulation.get(id=sim_id, query_criteria=query_criteria)


def get_all_experiments_for_user(user: str) -> List[Experiment]:
    """
    Returns all the experiments for a specific user.

    Args:
        user: username to locate

    Returns:
        Experiments for a user
    """
    # COMPS limits the retrieval to 1000 so to make sure we get all experiments for a given user, we need to be clever
    # Also COMPS does not have an order_by so we have to go through all date ranges
    interval = 365
    results = {}
    end_date = start_date = datetime.today()
    limit_date = datetime.strptime("2014-03-31", '%Y-%m-%d')  # Oldest simulation in COMPS

    while start_date > limit_date:
        start_date = end_date - timedelta(days=interval)
        batch = Experiment.get(query_criteria=QueryCriteria().where(["owner={}".format(user),
                                                                     "date_created<={}".format(
                                                                         end_date.strftime('%Y-%m-%d')),
                                                                     "date_created>={}".format(
                                                                         start_date.strftime('%Y-%m-%d'))]))
        if len(batch) == 1000:
            # We hit a limit, reduce the interval and run again
            interval = interval / 2
            continue

        if len(batch) == 0:
            interval *= 2
        else:
            # Add the experiments to the dict
            for e in batch:
                results[e.id] = e

        # Go from there
        end_date = start_date

    return list(results.values())


def get_simulations_from_big_experiments(experiment_id):
    """
    Get simulation for large experiment. This allows us to pull simulations in chunks.

    Args:
        experiment_id: Experiment id to load

    Returns:
        List of simulations
    """
    e = get_experiment_by_id(experiment_id)
    start_date = end_date = e.date_created
    import pytz
    limit_date = datetime.today().replace(tzinfo=pytz.utc)
    interval = 60
    stop_flag = False
    results = {}
    while start_date < limit_date:
        start_date = end_date + timedelta(minutes=interval)
        try:
            batch = Simulation.get(query_criteria=QueryCriteria()
                                   .select(['id', 'state', 'date_created']).select_children('tags')
                                   .where(["experiment_id={}".format(experiment_id),
                                           "date_created>={}".format(end_date.strftime('%Y-%m-%d %T')),
                                           "date_created<={}".format(start_date.strftime('%Y-%m-%d %T'))])
                                   )
        except Exception as e:
            logger.exception(e)
            interval /= 2
            continue

        if not batch:
            if stop_flag:
                break
            else:
                interval = 120
                stop_flag = True
        else:
            stop_flag = False
            for s in batch:
                results[s.id] = s
        end_date = start_date
    return results.values()
