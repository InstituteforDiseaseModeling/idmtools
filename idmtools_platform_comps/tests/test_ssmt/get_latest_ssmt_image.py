import os
import sys
import requests
from natsort import natsorted
from requests.auth import HTTPBasicAuth
from logging import getLogger
import keyring
from getpass import getpass

BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools/comps_ssmt_worker'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'
KEYRING_NAME = "idmtools_ssmt_builder"

logger = getLogger(__name__)


def get_username_and_password(disable_keyring_load=False, disable_keyring_save=False):
    """
    Try to get username.

    It first attempts loading from environment vars, then keyring if not disabled, then lastly prompts.

    Args:
        disable_keyring_load: Disable loading credentials from keyring
        disable_keyring_save: Disable keyring save

    Returns:
        Username password
    """
    # if 'PYPI_STAGING_USERNAME' in os.environ:
    #     logger.info("Loading Credentials from environment")
    #     if 'PYPI_STAGING_PASSWORD' not in os.environ:
    #         logger.error("When specifying username from environment variable, you must also specify password")
    #         sys.exit(-1)
    #     username = os.environ['PYPI_STAGING_USERNAME']
    #     password = os.environ['PYPI_STAGING_PASSWORD']
    # elif not disable_keyring_load and keyring.get_credential(KEYRING_NAME, "username"):
    #     username = keyring.get_password(KEYRING_NAME, "username")
    #     password = keyring.get_password(KEYRING_NAME, "password")
    # else:
    #     username = input('Username:')
    #     password = getpass(prompt='Password:')
    #     if not disable_keyring_save:
    #         logger.info("Saving Credentials")
    #         keyring.set_password(KEYRING_NAME, "username", username)
    #         keyring.set_password(KEYRING_NAME, "password", password)
    username="idm_bamboo_user@idmod.org"
    password='AKCp5dLMtaVQFvC6qzQz7a2gg8uvRN3kShgsxXj59UcgiBfBTjXW3kwuiM5iNnUMpBdUxz33u'
    return username, password


def get_latest_image_stage():
    username, password = get_username_and_password()
    auth = HTTPBasicAuth(username=username, password=password)
    response = requests.get(f'https://{BASE_REPO}/artifactory/api/docker/{REPO_KEY}/v2/{IMAGE_NAME}/tags/list',
                            auth=auth)
    if response.status_code == 200:
        images = natsorted(response.json()['tags'], reverse=True)
        images = [i for i in images if len(i) > 6]
        last_version = images[0]
        return last_version
    else:
        return None