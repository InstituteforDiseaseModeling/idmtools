import logging
from typing import Optional, Tuple, List, Dict, Any
from idmtools_platform_local.client.base import BaseClient
from idmtools_platform_local.config import API_PATH
from idmtools_platform_local.status import Status


logger = logging.getLogger(__name__)


class SimulationsClient(BaseClient):
    base_url = f'{API_PATH}/simulations'

    @classmethod
    def get_all(cls, experiment_id: Optional[str] = None, status: Optional[Status] = None,
                tags: Optional[List[Tuple[str, str]]] = None) -> List[Dict[str, Any]]:
        """

        Args:
            id (Optional[str]):  ID of the simulation
            experiment_id (Optional[str]): ID of experiments
            status (Optional[Status]): Optional status
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            List[Dict[str, Any]]: return list of simulations
        """
        args = cls._get_arguments(tags)
        args.update(dict(experiment_id=experiment_id))
        response = cls.get(None, params=args)
        result = cls._validate_response(response, 'Simulations')
        return result

    @classmethod
    def get_one(cls, id: str, experiment_id: Optional[str] = None, status: Optional[Status] = None,
                tags: Optional[List[Tuple[str, str]]] = None)\
            -> Dict[str, Any]:
        """
         Args:
            id (str):  ID of the simulation
            experiment_id (Optional[str]): ID of experiments
            status (Optional[Status]): Optional status
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            Dict[str, Any]: the simulation as a dict
        """
        args = cls._get_arguments(tags)
        args.update(dict(experiment_id=experiment_id))
        response = cls.get(id, params=args)
        result = cls._validate_response(response, 'Simulations')
        return result

    @classmethod
    def cancel(cls, id: str) -> Dict[str, Any]:
        """
        Marks a simulation to be canceled. Canceled jobs are only truly canceled when the queue message is processed
        Args:
            id (st):

        Returns:

        """
        data = cls.get_one(id)
        data['status'] = 'canceled'
        response = cls.put(id, data=data)
        if response.status_code != 200:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug(f'Updating  {cls.base_url if id is None else cls.base_url + "/" + id}'
                              f'Response Status Code: {response.status_code}. Response Content: {response.text}')
            raise RuntimeError(f'Could not fetch simulations from IDMs Local '
                               f'URL {cls.base_url if id is None else cls.base_url + "/" + id}')
        result = response.json()
        return result
