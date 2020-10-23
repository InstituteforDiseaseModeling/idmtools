import functools
import os
import json
from logging import getLogger
from typing import Optional, List
from urllib import request
import requests
from pkg_resources import parse_version
from packaging.version import parse
from html.parser import HTMLParser

IDM_DOCKER_PROD = 'https://packages.idmod.org/artifactory/list/docker-production/idmtools/'
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


def get_latest_package_version_from_artifactory(pkg_name, display_all=False):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
    Returns: the latest version of ven package
    """
    pkg_path = 'https://packages.idmod.org/artifactory/list/idm-pypi-production/'
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
    pkg_path = IDM_DOCKER_PROD
    pkg_url = os.path.join(pkg_path, pkg_name)
    return get_latest_version_from_site(pkg_url, base_version, display_all)


@functools.lru_cache(1)
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
