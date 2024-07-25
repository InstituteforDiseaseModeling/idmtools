"""This is a workaround script to get docker versions working with pip versions and to automate build of those images.

Copyright 2024, Bill Gates Foundation. All rights reserved.
"""
import os
import subprocess
import sys
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from natsort import natsorted

CURRENT_DIRECTORY = os.path.dirname(__file__)
BASE_VERSION = open(os.path.join(CURRENT_DIRECTORY, 'BASE_VERSION')).read().strip()
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'container-rocky-runtime'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/idmtools'

if 'PYPI_STAGING_USERNAME' in os.environ:
    username = os.environ['PYPI_STAGING_USERNAME']
else:
    print("Username:")
    username = input('Username:')
if 'PYPI_STAGING_PASSWORD' in os.environ:
    password = os.environ['PYPI_STAGING_PASSWORD']
else:
    password = getpass(prompt='Password:')
auth = HTTPBasicAuth(username=username, password=password)
response = requests.get(f'https://{BASE_REPO}/artifactory/api/docker/{REPO_KEY}/v2/idmtools/{IMAGE_NAME}/tags/list', auth=auth)
if response.status_code == 200:
    images = natsorted(response.json()['tags'], reverse=True)
    images = [i for i in images if len(i) >= 5]
    last_version = images[0]
    version_parts = last_version.split('.')
    base_part = '.'.join(version_parts[:-1])
    if BASE_VERSION in base_part:
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        version = '.'.join(version_parts)
    else:
        version = f'{BASE_VERSION}.0'
elif response.status_code == 404:
    version = f'{BASE_VERSION}.0'
else:
    print(response.content)
    raise Exception('Could not load images')

cmd = ['docker', 'push', f'{BASE_IMAGE_NAME}/{IMAGE_NAME}:{version}']
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
sys.exit(p.returncode)
