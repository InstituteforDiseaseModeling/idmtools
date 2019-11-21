import logging
import requests
from logging import getLogger
from idmtools_platform_local.config import get_api_path

logger = getLogger(__name__)


class BaseClient:
    base_url = get_api_path()

    @classmethod
    def _validate_response(cls, response, error_obj_str, id=None):
        if response.status_code == 404:
            raise FileNotFoundError(f"Could not find item with id of {id}")
        if response.status_code != 200:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug(
                    f'Error fetching {error_obj_str} {cls.base_url if id is None else cls.base_url + "/" + id}'
                    f'Response Status Code: {response.status_code}. Response Content: {response.text}')
            data = response.json()
            raise RuntimeError(data['message'])
        result = response.json()
        return result

    @classmethod
    def _get_arguments(cls, tags):
        args = dict(tags=tags if tags is not None and len(tags) > 0 else None)
        # Filter our any parameters set to None
        args = {k: v for k, v in args.items() if v is not None}
        # collapse tags to strings
        if 'tags' in args:
            # we need our tags in tuples then we can join properly and pass as GET array
            # so let's convert any input dict to tuples
            if type(args['tags']) is dict:
                args['tags'] = [(str(k), str(v)) for k, v in args['tags'].items()]
            args['tags'] = [','.join(tag) for tag in args['tags']]
        return args

    @classmethod
    def get(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.get(url, **kwargs)

    @classmethod
    def post(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.post(url, **kwargs)

    @classmethod
    def put(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.put(url, **kwargs)

    @classmethod
    def delete(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.delete(url, **kwargs)
