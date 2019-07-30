import logging
from typing import Optional, Tuple, List, Dict, Any
from idmtools_local.client.base import BaseClient
from idmtools_local.config import API_PATH
from idmtools_local.status import Status


logger = logging.getLogger(__name__)


class SimulationsClient(BaseClient):
    base_url = f'{API_PATH}/simulations'

    @classmethod
    def get_all(cls, id: Optional[str] = None, experiment_id: Optional[str] = None, status: Optional[Status] = None,
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
        args = dict(experiment_id=experiment_id,
                    status=str(status) + 'a' if status is not None else status,
                    tags=tags if tags is not None and len(tags) > 0 else None)
        args = {k: v for k, v in args.items() if v is not None}
        # collapse tags to strings
        if 'tags' in args:
            # we need our tags in tuples then we can join properly and pass as GET array
            # so let's convert any input dict to tuples
            if type(args['tags']) is dict:
                args['tags'] = [(str(k), str(v)) for k, v in args['tags'].items()]
            args['tags'] = [','.join(tag) for tag in args['tags']]
        response = cls.get(id, params=args)
        if response.status_code != 200:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug(f'Error fetching simulations {cls.base_url if id is None else cls.base_url + "/" + id}'
                              f'Response Status Code: {response.status_code}. Response Content: {response.text}')
            data = response.json()
            raise RuntimeError(data['message'])
        result = response.json()
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
        result = cls.get_all(id, experiment_id, status, tags)
        if len(result) == 0:
            raise RuntimeError(f"Could not find Simulation with ID {id}")
        return result[0]

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
