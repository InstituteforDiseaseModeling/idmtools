"""idmtools local platform simulations API Client.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
from typing import Optional, Tuple, List, Dict, Any
from idmtools_platform_local.client.base import BaseClient
from idmtools_platform_local.status import Status


logger = logging.getLogger(__name__)


class SimulationsClient(BaseClient):
    """
    Provide API client for Simulations.
    """
    path_url = 'simulations'

    @classmethod
    def get_all(cls, experiment_id: Optional[str] = None, status: Optional[Status] = None,
                tags: Optional[List[Tuple[str, str]]] = None, page: Optional[int] = None, per_page: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all simulation matcher a criteria.

        Args:
            experiment_id: ID of the simulation
            status: Optional status
            tags:  List of tags/values to filter experiment by
            page: page
            per_page: items per page

        Returns:
            List[Dict[str, Any]]: return list of simulations
        """
        args = cls._get_arguments(tags)
        args.update(dict(experiment_id=experiment_id))
        if page:
            args['page'] = page

        if per_page:
            args['per_page'] = per_page
        response = cls.get(cls.path_url, params=args)
        result = cls._validate_response(response, 'Simulations')
        return result

    @classmethod
    def get_one(cls, simulation_id: str, experiment_id: Optional[str] = None, status: Optional[Status] = None,
                tags: Optional[List[Tuple[str, str]]] = None)\
            -> Dict[str, Any]:
        """
        Get one simulation.

         Args:
            simulation_id (str):  ID of the simulation
            experiment_id (Optional[str]): ID of experiments
            status (Optional[Status]): Optional status
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            Dict[str, Any]: the simulation as a dict
        """
        args = cls._get_arguments(tags)
        args.update(dict(experiment_id=experiment_id))
        response = cls.get(f'{cls.path_url}/{simulation_id}', params=args)
        result = cls._validate_response(response, 'Simulations', id=simulation_id)
        return result

    @classmethod
    def cancel(cls, simulation_id: str) -> Dict[str, Any]:
        """
        Marks a simulation to be canceled. Canceled jobs are only truly canceled when the queue message is processed.

        Args:
            simulation_id (st):

        Returns:
            Cancel result
        """
        data = cls.get_one(simulation_id)
        data['status'] = 'canceled'
        response = cls.put(f'{cls.path_url}/{simulation_id}', data=data)
        if response.status_code != 200:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug(
                    f'Updating  {cls.base_url if simulation_id is None else cls.base_url + "/" + simulation_id}'
                    f'Response Status Code: {response.status_code}. Response Content: {response.text}')
            raise RuntimeError(f'Could not fetch simulations from IDMs Local '
                               f'URL {cls.base_url if simulation_id is None else cls.base_url + "/" + simulation_id}')
        result = response.json()
        return result
