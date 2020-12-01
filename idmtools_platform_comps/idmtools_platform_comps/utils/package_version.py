import functools
import operator
import os
import json
from datetime import datetime
from logging import getLogger
from typing import Optional, List
from urllib import request
import requests
from pkg_resources import parse_version
from packaging.version import parse
from html.parser import HTMLParser

IDM_DOCKER_PROD = 'https://packages.idmod.org/artifactory/list/docker-production'
IDMTOOLS_DOCKER_PROD = f'{IDM_DOCKER_PROD}/idmtools/'
MANIFEST_URL = "https://hub.docker.com/v2/repositories/library/{repository}/tags/?page_size=25&page=1&name={tag}"

logger = getLogger(__name__)


class LinkHTMLParser(HTMLParser):
    previous_tag = None
    pkg_version = []

    def handle_starttag(self, tag, attrs):
        self.previous_tag = tag
        if tag != 'a':
            return

        attr = dict(attrs)
        v = attr['href']
        v = v.rstrip('/')
        self.pkg_version.append(v)


def get_latest_package_version_from_pypi(pkg_name, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    url = f'https://pypi.python.org/pypi/{pkg_name}/json'
    try:
        releases = json.loads(request.urlopen(url).read())['releases']
    except Exception:
        return None

    all_releases = sorted(releases, key=parse_version, reverse=True)

    if display_all:
        print(all_releases)

    release_versions = [ver for ver in all_releases if not parse(ver).is_prerelease]
    latest_version = release_versions[0]

    return latest_version


def get_latest_pypi_package_version_from_artifactory(pkg_name, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    pkg_path = 'https://packages.idmod.org/artifactory/api/pypi/pypi-production/simple'
    pkg_url = os.path.join(pkg_path, pkg_name)
    return get_latest_version_from_site(pkg_url, display_all)


def get_latest_ssmt_image_version_from_artifactory(pkg_name='comps_ssmt_worker', base_version: Optional[str] = None, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        base_version: Optional base version. Versions above this will not be added.
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    pkg_path = IDMTOOLS_DOCKER_PROD
    pkg_url = os.path.join(pkg_path, pkg_name)
    return get_latest_version_from_site(pkg_url, base_version, display_all)


def get_docker_manifest(image_path="idmtools/comps_ssmt_worker", repo_base=IDM_DOCKER_PROD):
    """
    Get docker manifest from IDM Artifactory. It mimics latest even when user has no latest tag degined

    Args:
        image_path:
        repo_base:

    Returns:

    """
    if ":" not in image_path:
        image_path += ":latest"

    path, tag = image_path.split(":")
    if tag == "latest":
        url = "/".join([IDM_DOCKER_PROD, path])
        response = requests.get(url)
        content = response.text
        lines = [link.split(">") for link in content.split("\n") if "<a href" in link and "pre" not in link]
        lines = {item_date[1].replace("/</a", ''): datetime.strptime(item_date[2].strip(" -"), '%d-%b-%Y %H:%M') for item_date in lines}
        tag = list(sorted(lines.items(), key=operator.itemgetter(1), reverse=True))[0][0]
        image_path = ":".join([path, tag])
    final_path = "/".join([path, tag, "manifest.json"])
    pkg_path = f'{repo_base}/{final_path}'
    response = requests.get(pkg_path)
    if response.status_code != 200:
        raise ValueError("Could not find manifest for file")
    return response.json(), image_path


def get_digest_from_docker_hub(repo, tag='latest'):
    """
     repo: string, repository (e.g. 'library/fedora')
     tag:  string, tag of the repository (e.g. 'latest')
     """

    response = requests.get(
        MANIFEST_URL.format(repository=repo, tag=tag),
        json=True,
    )
    manifest = response.json()
    if response.ok and manifest['count']:
        images = list(filter(lambda x: x['architecture'] == "amd64", manifest['results'][0]['images']))
        if len(images):
            return images[0]['digest']

    return None


@functools.lru_cache(8)
def fetch_versions_from_server(pkg_url: str) -> List[str]:
    """
    Fetch all versions from server

    Args:
        pkg_url: Url to fetch

    Returns:

    """
    resp = requests.get(pkg_url)
    if resp.status_code != 200:
        logger.warning('Could not fetch URL')
        return None

    html_str = resp.text

    parser = LinkHTMLParser()
    parser.feed(html_str)
    releases = parser.pkg_version
    releases = [v for v in releases if not v.startswith('.')]

    all_releases = sorted(releases, key=parse_version, reverse=True)
    return all_releases


@functools.lru_cache(3)
def get_latest_version_from_site(pkg_url, base_version: Optional[str] = None, display_all=False):
    """
    Utility to get the latest version for a given package name

    Args:
        pkg_url: package name given
        base_version: Optional base version. Versions above this will not be added.
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    all_releases = fetch_versions_from_server(pkg_url)
    if all_releases is None:
        raise ValueError(f"Could not determine latest version for package {pkg_url}. You can manually specify a version to avoid this error")

    if display_all:
        print(all_releases)

    release_versions = [ver for ver in all_releases if not parse(ver).is_prerelease]

    # comps_ssmt_worker will store only x.x.x.x
    if 'comps_ssmt_worker' in pkg_url.lower():
        release_versions = [ver for ver in release_versions if len(ver.split('.')) == 4]

    if base_version:
        # only use the longest match latest
        version_compatible_portion = ".".join(base_version.split(".")[:2])

        for ver in release_versions:
            if ".".join(ver.split('.')[:2]) == version_compatible_portion:
                return ver
        return None
    else:
        return release_versions[0] if release_versions else None
