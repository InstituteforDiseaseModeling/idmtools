"""This is a workaround script to get docker versions working with pip versions and to automate build of those images."""
import os
import subprocess
import sys
from getpass import getpass

import requests
from requests.auth import HTTPBasicAuth


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOCAL_PACKAGE_DIR = os.path.join(BASE_DIR, 'idmtools_platform_local')
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools/local_workers'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'

base_version = open('VERSION').read().strip()

print("Please be sure you are logged into the docker-production.packages.idmod.org Docker Repo")

# determine next version by querying artifactory
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
response = requests.get(f'https://{BASE_REPO}/artifactory/api/docker/{REPO_KEY}/v2/{IMAGE_NAME}/tags/list', auth=auth)

if response.status_code == 200:
    images = sorted(response.json()['tags'], reverse=True)
    images = [i for i in images if len(i) > 6 and 'nightly' not in i]
    last_version = images[0]
    if base_version in last_version and 'nightly' not in last_version:
        version_parts = last_version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        version = '.'.join(version_parts)
    else:
        version = f'{base_version}.0'
else:
    print(response.content)
    raise Exception('Could not load images')

# push full version
cmd = ['docker', 'push', f'{REPO_KEY}.{BASE_REPO}/{IMAGE_NAME}:{version}']
print(f'Running: {" ".join(cmd)}')
p1 = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p1.wait()

# push patch level latest
cmd = ['docker', 'push', f'{REPO_KEY}.{BASE_REPO}/{IMAGE_NAME}:{version[0:5]}']
# push to version as well
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
sys.exit(p.returncode)
