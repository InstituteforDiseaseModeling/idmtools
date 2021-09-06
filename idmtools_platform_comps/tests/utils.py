import os
from functools import wraps
from logging import getLogger
from urllib.parse import ParseResult, parse_qs

import allure
import pytest

FIXTURE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fixtures")
logger = getLogger()


def comps_decorate_test(feature, serial: bool = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper = allure.story(feature)(allure.story("COMPS")(pytest.mark.comps(wrapper)))
        return wrapper

    return decorator


def get_filename_url(url: ParseResult) -> str:
    """
    Convert a url to a fixture file path

    Args:
        url: Url to convert to file path

    Returns:
        Fixture file path for the url
    """
    path = os.path.join(FIXTURE_PATH, 'COMPSClient', url.path.replace("/", os.path.sep).strip(os.path.sep))
    if url.query:
        params = parse_qs(url.query)
        for param in sorted(params.keys()):
            path = os.path.join(path, param, params[param][0] if isinstance(params[param], list) else params[param])
    path += '.json'
    return path
