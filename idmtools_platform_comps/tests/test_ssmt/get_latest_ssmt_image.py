import requests
from natsort import natsorted
from requests.auth import HTTPBasicAuth

from ssmt_image.build_docker_image import get_username_and_password

BASE_REPO = 'packages.idmod.org'
REPO_KEY = 'idm-docker-staging'
DOCKER_REPO = f'{REPO_KEY}.{BASE_REPO}'
IMAGE_NAME = 'idmtools/comps_ssmt_worker'
BASE_IMAGE_NAME = f'{DOCKER_REPO}/{IMAGE_NAME}'


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