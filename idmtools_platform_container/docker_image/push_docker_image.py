"""This is the script to push docker image to idm staging artifactory.

Copyright 2024, Bill Gates Foundation. All rights reserved.
"""
import argparse
import os
import subprocess
import sys
from logging import getLogger, basicConfig, DEBUG, INFO
current_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_directory))
from build_docker_image import get_username_and_password, get_latest_image_version_from_registry  # noqa: E402

current_working_directory = os.getcwd()
BASE_VERSION = open(os.path.join(current_working_directory, 'BASE_VERSION')).read().strip()
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/idmtools'

logger = getLogger(__name__)


def push_image(username, password, dockerfile, image_name, disable_keyring_load, disable_keyring_save):
    """
    Push docker image to idm staging artifactory.

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
    cmd = ['docker', 'push', f'{BASE_IMAGE_NAME}/{image_name}:{version}']
    print(f'Running: {" ".join(cmd)}')
    p = subprocess.Popen(" ".join(cmd), cwd=current_working_directory, shell=True)
    p.wait()
    sys.exit(p.returncode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Publish Container Image to Artifactory")
    parser.add_argument("--username", default=None, help="Docker Staging Username")
    parser.add_argument("--password", default=None, help="Docker Staging Password")
    parser.add_argument("--dockerfile", default="Dockerfile", help="Dockerfile to use for building image")
    parser.add_argument("--image_name", default="container-rocky-runtime", help="image name to use for building image")
    parser.add_argument("--disable-keyring-load", default=False, help="Disable loading password from keyring")
    parser.add_argument("--disable-keyring-save", default=False, help="Disable saving password to keyring after user prompts")
    parser.add_argument("--verbose", default=False, help="Enable Debug logging")
    parser.add_argument("--debug", default=False, help="Enable Debug logging")
    args = parser.parse_args()

    basicConfig(filename="build.log", level=DEBUG if any([args.verbose, args.debug]) else INFO)
    push_image(args.username, args.password, args.dockerfile, args.image_name, args.disable_keyring_load, args.disable_keyring_save)
