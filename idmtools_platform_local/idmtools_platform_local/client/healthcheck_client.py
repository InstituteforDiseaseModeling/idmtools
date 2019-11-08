import logging
from typing import Optional, Tuple, List, Dict, Any
from idmtools_platform_local.client.base import BaseClient

logger = logging.getLogger(__name__)


class HealthcheckClient(BaseClient):
    path_url = 'healthcheck'

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        """
        Get all experiments with options to filter by tags

        Args:
            per_page: How many experiments to return per page
            page: Which page
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            List[Dict[str, Any]]: returns list of experiments
        """

        response = cls.get(cls.path_url)
        result = cls._validate_response(response, 'Experiments')
        return result

    @classmethod
    def get_one(cls) -> Dict[str, Any]:
        """
        Convenience method to get one experiment

        Args:
            id (str):  ID of the experiment
            tags (Optional[List[Tuple[str, str]]]): List of tags/values to filter experiment by

        Returns:
            dict: Dictionary containing the experiment objects
        """
        return cls.get_all()

    @classmethod
    def delete(cls, *args, **kwargs) -> bool:
        raise NotImplementedError("Healthcheck does not support delete")

    @classmethod
    def post(cls, *args, **kwargs) -> bool:
        raise NotImplementedError("Healthcheck does not support delete")
