"""This is a workaround script to get docker versions working with pip versions and to automate build of those images.
Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import argparse
import os
import subprocess
import sys

from build_docker_image import get_latest_image_version_from_registry

base_version = open('VERSION').read().strip()
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools/rocky_mpi_docker/dtk_run_rocky_py39'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'



def publish_image(username, password):
    version = get_latest_image_version_from_registry(username, password)
    cmd = ['docker', 'push', f'{BASE_IMAGE_NAME}:{version}']
    print(f'Running: {" ".join(cmd)}')
    p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
    p.wait()
    sys.exit(p.returncode)


if __name__ == "__main__":
    # Usage: python publish_docker_image.py --username username --password password
    parser = argparse.ArgumentParser("Build docker Image")
    parser.add_argument("--username", default=None, help="Docker Production Username")
    parser.add_argument("--password", default=None, help="Docker Production Password")
    args = parser.parse_args()
    publish_image(args.username, args.password)