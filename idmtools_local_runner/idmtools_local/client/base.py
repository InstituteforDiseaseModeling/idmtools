import requests

from idmtools_local.config import API_PATH


class BaseClient:
    base_url = API_PATH

    @classmethod
    def get(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.get(url, **kwargs)

    @classmethod
    def post(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.get(url, **kwargs)

    @classmethod
    def put(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.get(url, **kwargs)

    @classmethod
    def delete(cls, path, **kwargs) -> requests.Response:
        url = f'{cls.base_url}/{path}' if path is not None else cls.base_url
        return requests.get(url, **kwargs)