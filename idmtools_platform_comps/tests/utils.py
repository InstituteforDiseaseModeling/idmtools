import json
import os
from logging import getLogger
from urllib.parse import urlparse, ParseResult, parse_qs

import responses
from requests import Request, Session

FIXTURE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "fixtures")
logger = getLogger()


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


def load_fixture(request: Request, create_if_not_exist: bool = False, overwrite_fixtures: bool = False):
    """
    Load Fixture from a Request object. Also can create fixtures

    Args:
        request: Request object to load
        create_if_not_exist: If the fixture does not exist, should we create it?
        overwrite_fixtures: Write fixture even if it exists

    Returns:
        Response containing fixture data
    Raise:
        ValueError - When the url fails
        FileNotFoundError - If the fixture cannot be found and creating fixtures is disabled
    """
    url = urlparse(request.url)
    path = get_filename_url(url)
    if os.path.exists(path) and not overwrite_fixtures:
        logger.info(f'Loading fixture from {path}')
        with open(path, 'r') as jsrc:
            return 200, dict(), jsrc.read()
    else:
        if create_if_not_exist:
            logger.debug(f'{path} does not exist so creating')
            odir = os.path.dirname(path)
            logger.debug(f'Ensuring {odir} exists')
            os.makedirs(odir, exist_ok=True)
            s = Session()
            responses.stop()
            response = s.send(request)
            responses.start()
            if response.status_code == 200:
                logger.debug(f'Writing response to {path}')
                with open(path, 'wb') as fout:
                    fout.write(response.content)
                return 200, dict(), response.content
            else:
                raise ValueError(f'{response.status_code} - {response.text}')
        raise FileNotFoundError(f"Could not find the fixture for {request.url}")