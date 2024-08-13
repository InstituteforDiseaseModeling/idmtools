"""This script is used to build a docker image for the idmtools_platform_container.

Copyright 2024, Bill Gates Foundation. All rights reserved.
"""
import argparse
import os
import subprocess
import sys
import requests
import keyring
from logging import getLogger, basicConfig, DEBUG, INFO
from getpass import getpass
from requests.auth import HTTPBasicAuth
from natsort import natsorted


logger = getLogger(__name__)
# Global Configurations
KEYRING_NAME = "idmtools_container_docker_builder"
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/idmtools'
current_working_directory = os.getcwd()
BASE_VERSION = open(os.path.join(current_working_directory, 'BASE_VERSION')).read().strip()

logger.info("Please be sure you are logged into the docker-production.packages.idmod.org Docker Repo")


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
    return username, password


def get_latest_image_version_from_registry(username, password, image_name):
    """
    Fetch the latest image version from repo.
    Args:
        username: Username to use with registry
        password: Password to use with registry
        image_name: Docker image name to use for building image
    Returns:
        Latest version published in the registry
    """
    url = f'https://{BASE_REPO}/artifactory/api/docker/{REPO_KEY}/v2/idmtools/{image_name}/tags/list'
    auth = HTTPBasicAuth(username=username, password=password)
    logger.info(f"Loading Credentials from {url}")
    response = requests.get(url, auth=auth)
    logger.debug(f"Return Code: {response.status_code}")
    if response.status_code != 200 and response.status_code != 404:
        print(response.status_code)
        print(response.content)
        raise Exception('Could not load images')
    elif response.status_code == 404:
        logger.info(f"First Version {url}")
        return f'{BASE_VERSION}.0'
    else:
        images = natsorted(response.json()['tags'], reverse=True)
        images = [i for i in images if len(i) >= 5]
        logger.debug(f"Images: {images}")
        last_version = images[0]
        logger.info(f"Last Version {url}")
        version_parts = last_version.split('.')
        base_part = '.'.join(version_parts[:-1])
        if BASE_VERSION in base_part:
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            version = '.'.join(version_parts)
        else:
            version = f'{BASE_VERSION}.0'
        logger.info(f"Next Version: {version}")
        return version


def build_image(username, password, dockerfile, image_name, disable_keyring_load, disable_keyring_save):
    """
    Run the docker build command.

    Args:
        username: Username to use with registry
        password: Password to use with registry
        dockerfile: Dockerfile to use for building image
        image_name: Docker image name to use for building image
        disable_keyring_load: Disable keyring which caches passwords
        disable_keyring_save: Disable caching password to the keyring

    Returns:
        None
    """
    if username is None or password is None:
        username, password = get_username_and_password(disable_keyring_load, disable_keyring_save)
    version = get_latest_image_version_from_registry(username, password, image_name)
    cmd = ['docker', 'build', '--network=host', '--build-arg', f'CONTAINER_VERSION={version}', '--tag',
           f'{BASE_IMAGE_NAME}/{image_name}:{version}', '-f', dockerfile, '.']
    logger.info(f'Running: {" ".join(cmd)}')
    p = subprocess.Popen(" ".join(cmd), cwd=current_working_directory, shell=True)
    p.wait()

    if p.returncode == 0:
        logger.info("Tagging image")
        os.system(f'docker tag {BASE_IMAGE_NAME}/{image_name}:{version} {BASE_IMAGE_NAME}/{image_name}:{version[:-2]}')
    sys.exit(p.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Build Container Image")
    parser.add_argument("--username", default=None, help="Docker Production Username")
    parser.add_argument("--password", default=None, help="Docker Production Password")
    parser.add_argument("--dockerfile", default="Dockerfile", help="Dockerfile to use for building image")
    parser.add_argument("--image_name", default="container-rocky-runtime", help="image name to use for building image")
    parser.add_argument("--disable-keyring-load", default=False, help="Disable loading password from keyring")
    parser.add_argument("--disable-keyring-save", default=False, help="Disable saving password to keyring after user prompts")
    parser.add_argument("--verbose", default=False, help="Enable Debug logging")
    parser.add_argument("--debug", default=False, help="Enable Debug logging")
    args = parser.parse_args()

    basicConfig(filename="build.log", level=DEBUG if any([args.verbose, args.debug]) else INFO)
    build_image(args.username, args.password, args.dockerfile, args.image_name, args.disable_keyring_load, args.disable_keyring_save)
