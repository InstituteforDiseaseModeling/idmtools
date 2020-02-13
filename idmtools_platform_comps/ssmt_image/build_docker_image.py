####
# This script is currently a workaround so that we can use bump2version with docker since the nightly versions
# don't work with docker registry
import os
import subprocess
import sys
from getpass import getpass
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse

BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools_comps_ssmt_worker'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'

base_version = open('../VERSION').read().strip()

# determine next version by querying artifactory
if 'bamboo_UserArtifactory' in os.environ:
    username = os.environ['bamboo_UserArtifactory']
else:
    username = input('Username:')
if 'bamboo_PasswordArtifactory' in os.environ:
    password = os.environ['bamboo_PasswordArtifactory']
else:
    password = getpass(prompt='Password:')
auth = HTTPBasicAuth(username=username, password=password)
response = requests.get(f'https://{BASE_REPO}/api/docker/{REPO_KEY}/v2/{IMAGE_NAME}/tags/list', auth=auth)
if response.status_code == 200:
    images = sorted(response.json()['tags'], reverse=True)
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


print(f'PIP URL: {sys.argv[1]}')
uri = urlparse(sys.argv[1])

cmd = ['docker', 'build', '--network=host', '--build-arg', f'PYPIURL={sys.argv[1]}', '--build-arg',
       f'PYPIHOST={uri.hostname}', '--tag', f'{DOCKER_REPO}/{IMAGE_NAME}:{version}', '.']
if len(sys.argv) == 3 and sys.argv[2] == "no-cache":
    cmd.insert(2, "--no-cache")
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
if p.returncode == 0:
    os.system(f'docker tag {DOCKER_REPO}/{IMAGE_NAME}:{version} {DOCKER_REPO}/{IMAGE_NAME}:{version[:2]}')
sys.exit(p.returncode)
