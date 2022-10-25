"""idmtools local platform experiment API Client.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
from typing import Optional, Tuple, List, Dict, Any
from idmtools_platform_local.client.base import BaseClient

logger = logging.getLogger(__name__)


class ExperimentsClient(BaseClient):
    """Provides API client for Experiments."""
    path_url = 'experiments'

    @classmethod
    def get_all(cls, tags: Optional[List[Tuple[str, str]]] = None,
                page: Optional[int] = None, per_page: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all experiments with options to filter by tags.

        Args:
            per_page: How many experiments to return per page
            page: Which page
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            List[Dict[str, Any]]: returns list of experiments
        """
        args = cls._get_arguments(tags)

        if page:
            args['page'] = page

        if per_page:
            args['per_page'] = per_page

        response = cls.get(cls.path_url, params=args)
        result = cls._validate_response(response, 'Experiments')
        return result

    @classmethod
    def get_one(cls, id: str, tags: Optional[List[Tuple[str, str]]] = None) -> Dict[str, Any]:
        """
        Convenience method to get one experiment.

        Args:
            id (str):  ID of the experiment
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            dict: Dictionary containing the experiment objects
        """
        args = cls._get_arguments(tags)
        response = cls.get(f'{cls.path_url}/{id}', params=args)
        result = cls._validate_response(response, 'Experiments', id=id)
        return result

    @classmethod
    def delete(cls, id: str, delete_data: bool = False, ignore_doesnt_exist: bool = True) -> bool:
        """
        Delete an experiment. Optionally you can delete the experiment data. WARNING: Deleting the data is irreversible.

        Args:
            id (str): ID of the experiments
            delete_data (bool): Delete data directory including simulations
            ignore_doesnt_exist: Ignore error if the specific experiment doesn't exist

        Returns:
            True if deletion is succeeded
        """
        params = dict()
        if delete_data:
            params['data'] = True
        response = super().delete(f'{cls.path_url}/{id}', params=params)

        if response.status_code != 204 and (response.status_code != 404 and ignore_doesnt_exist):
            return False
        elif response.status_code != 204:
            data = response.json()
            raise RuntimeError(data['message'])
        return True
