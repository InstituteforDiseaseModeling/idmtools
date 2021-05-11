"""This is a workaround script to get docker versions working with pip versions and to automate build of those images.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import subprocess
import sys
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from natsort import natsorted

base_version = open('../VERSION').read().strip()
BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools/comps_ssmt_worker'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'

if 'bamboo_UserArtifactory' in os.environ:
    username = os.environ['bamboo_UserArtifactory']
else:
    print("Username:")
    username = input('Username:')
if 'bamboo_PasswordArtifactory' in os.environ:
    password = os.environ['bamboo_PasswordArtifactory']
else:
    password = getpass(prompt='Password:')
auth = HTTPBasicAuth(username=username, password=password)
response = requests.get(f'https://{BASE_REPO}/artifactory/api/docker/{REPO_KEY}/v2/{IMAGE_NAME}/tags/list', auth=auth)
if response.status_code == 200:
    images = natsorted(response.json()['tags'], reverse=True)
    images = [i for i in images if len(i) > 6]
    last_version = images[0]
    if base_version in last_version:
        version_parts = last_version.split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        version = '.'.join(version_parts)
    else:
        version = f'{base_version}.0'
else:
    print(response.content)
    raise Exception('Could not load images')

cmd = ['docker', 'push', f'{REPO_KEY}.{BASE_REPO}/idmtools/comps_ssmt_worker:{version}']
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
sys.exit(p.returncode)
