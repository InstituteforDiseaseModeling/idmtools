"""idmtools local platform healthcheck API Client.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import logging
from typing import List, Dict, Any
from idmtools_platform_local.client.base import BaseClient

logger = logging.getLogger(__name__)


class HealthcheckClient(BaseClient):
    """Provides Healthcheck API client."""
    path_url = 'healthcheck'

    @classmethod
    def get_all(cls) -> List[Dict[str, Any]]:
        """
        Get all health check info.

        Returns:
            List[Dict[str, Any]]: returns list of experiments
        """
        response = cls.get(cls.path_url)
        result = cls._validate_response(response, 'Experiments')
        return result

    @classmethod
    def get_one(cls) -> Dict[str, Any]:
        """
        Convenience method to get one specific healthcheck.

        Returns:
            dict: Dictionary containing the experiment objects
        """
        return cls.get_all()

    @classmethod
    def delete(cls, *args, **kwargs) -> bool:
        """Delete request."""
        raise NotImplementedError("Healthcheck does not support delete")

    @classmethod
    def post(cls, *args, **kwargs) -> bool:
        """Post request."""
        raise NotImplementedError("Healthcheck does not support delete")
