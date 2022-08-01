"""This script is currently a workaround so that we can use bump2version with docker since the nightly versions doesn't work with docker registry.

Notes:
    If you are using this script locally, you need to set the environment variables *PYPI_STAGING_USERNAME* and *PYPI_STAGING_PASSWORD*.
    These can be set to your idm email/password

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import argparse
import glob
import os
import shutil
import subprocess
from logging import getLogger, basicConfig, DEBUG, INFO
import sys
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
import keyring
from natsort import natsorted


logger = getLogger(__name__)
# Global Configurations
KEYRING_NAME = "idmtools_ssmt_builder"
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools/comps_ssmt_worker'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'
CURRENT_DIRECTORY = os.path.dirname(__file__)
BASE_VERSION = open(os.path.join(CURRENT_DIRECTORY, '..', 'VERSION')).read().strip()

logger.info("Please be sure you are logged into the docker-production.packages.idmod.org Docker Repo")
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIRECTORY, '..', '..'))
LOCAL_PACKAGE_DIR = os.path.join(BASE_DIR, 'idmtools_platform_comps/ssmt_image')


def get_dependency_packages():
    """
    Get python packages required to build image.

    Returns:
        None
    """
    os.makedirs(os.path.abspath('.depends'), exist_ok=True)
    for root, _dirs, files in os.walk(os.path.join(LOCAL_PACKAGE_DIR, '.depends')):
        for file in files:
            os.remove(os.path.join(root, file))
    for package in ['idmtools_core', 'idmtools_models', 'idmtools_platform_comps']:
        for file in glob.glob(os.path.join(BASE_DIR, package, 'dist', '**.gz')):
            shutil.copy(file, os.path.join(LOCAL_PACKAGE_DIR, '.depends', os.path.basename(file)))


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
    if 'PYPI_STAGING_USERNAME' in os.environ:
        logger.info("Loading Credentials from environment")
        if 'PYPI_STAGING_PASSWORD' not in os.environ:
            logger.error("When specifying username from environment variable, you must also specify password")
            sys.exit(-1)
        username = os.environ['PYPI_STAGING_USERNAME']
        password = os.environ['PYPI_STAGING_PASSWORD']
    elif not disable_keyring_load and keyring.get_credential(KEYRING_NAME, "username"):
        username = keyring.get_password(KEYRING_NAME, "username")
        password = keyring.get_password(KEYRING_NAME, "password")
    else:
        username = input('Username:')
        password = getpass(prompt='Password:')
        if not disable_keyring_save:
            logger.info("Saving Credentials")
            keyring.set_password(KEYRING_NAME, "username", username)
            keyring.set_password(KEYRING_NAME, "password", password)
    username = 'shchen@idmod.org'
    password="Hongminc914211914211"
    return username, password


def get_latest_image_version_from_registry(username, password):
    """
    Fetch the latest image version from repo.

    Returns:
        Latest version published in the registry
    """
    url = f'https://{BASE_REPO}/artifactory/api/docker/{REPO_KEY}/v2/{IMAGE_NAME}/tags/list'
    auth = HTTPBasicAuth(username=username, password=password)
    logger.info(f"Loading Credentials from {url}")
    response = requests.get(url, auth=auth)
    logger.debug(f"Return Code: {response.status_code}")
    if response.status_code != 200:
        print(response.status_code)
        print(response.content)
        raise Exception('Could not load images')
    else:
        images = natsorted(response.json()['tags'], reverse=True)
        images = [i for i in images if len(i) > 6]
        logger.debug(f"Images: {images}")
        last_version = images[0]
        logger.info(f"Last Version {url}")
        if BASE_VERSION in last_version:
            version_parts = last_version.split('.')
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            version = '.'.join(version_parts)
        else:
            version = f'{BASE_VERSION}.0'
        logger.info(f"Next Version: {version}")
        return version


def build_image(username, password, disable_keyring_load, disable_keyring_save):
    """
    Run the docker build command.

    Args:
        username: Username to use with registry
        password: Password to use with registry
        disable_keyring_load: Disable keyring which caches passwords
        disable_keyring_save: Disable caching password to the keyring

    Returns:
        None
    """
    if username is None or password is None:
        username, password = get_username_and_password(disable_keyring_load, disable_keyring_save)
    get_dependency_packages()
    version = get_latest_image_version_from_registry(username, password)
    cmd = ['docker', 'build', '--network=host', '--build-arg', f'SSMT_VERSION={version}', '--tag',
           f'{DOCKER_REPO}/{IMAGE_NAME}:{version}', '.']
    logger.info(f'Running: {" ".join(cmd)}')
    p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
    p.wait()

    if p.returncode == 0:
        logger.info("Tagging image")
        os.system(f'docker tag {DOCKER_REPO}/{IMAGE_NAME}:{version} {DOCKER_REPO}/{IMAGE_NAME}:{version[:-2]}')
    sys.exit(p.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Build SSMT Image")
    parser.add_argument("--username", default=None, help="Docker Production Username")
    parser.add_argument("--password", default=None, help="Docker Production Password")
    parser.add_argument("--disable-keyring-load", default=False, help="Disable loading password from keyring")
    parser.add_argument("--disable-keyring-save", default=False, help="Disable saving password to keyring after user prompts")
    parser.add_argument("--verbose", default=False, help="Enable Debug logging")
    parser.add_argument("--debug", default=False, help="Enable Debug logging")
    args = parser.parse_args()

    basicConfig(filename="build.log", level=DEBUG if any([args.verbose, args.debug]) else INFO)
    build_image(args.username, args.password, args.disable_keyring_load, args.disable_keyring_save)
