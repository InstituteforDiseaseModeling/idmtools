import functools
import operator
import json
import re
from abc import ABC
from datetime import datetime
from logging import getLogger, DEBUG
from typing import Optional, List, Type
from urllib import request
import requests
from pkg_resources import parse_version
from packaging.version import parse
from html.parser import HTMLParser

PYPI_PRODUCTION_SIMPLE = 'https://packages.idmod.org/artifactory/api/pypi/pypi-production/simple'

IDM_DOCKER_PROD = 'https://packages.idmod.org/artifactory/list/docker-production'
IDMTOOLS_DOCKER_PROD = f'{IDM_DOCKER_PROD}/idmtools/'
MANIFEST_URL = "https://hub.docker.com/v2/repositories/library/{repository}/tags/?page_size=25&page=1&name={tag}"

logger = getLogger(__name__)


class PackageHTMLParser(HTMLParser, ABC):
    previous_tag = None
    pkg_version = None

    def __init__(self):
        super().__init__()
        self.pkg_version = set()


class LinkHTMLParser(PackageHTMLParser):

    def handle_starttag(self, tag, attrs):
        self.previous_tag = tag
        if tag != 'a':
            return

        attr = dict(attrs)
        v = attr['href']
        v = v.rstrip('/')
        self.pkg_version.add(v)


class LinkNameParser(PackageHTMLParser):
    in_link = False
    ver_pattern = re.compile(r'^[\d\.brcdev\+nightly]+$')

    def handle_starttag(self, tag, attrs):
        self.previous_tag = tag
        self.in_link = tag == "a"

    def handle_endtag(self, tag):
        if tag == "a":
            self.in_link = False

    def handle_data(self, data):
        if self.in_link:
            parts = data.split("-")
            if len(parts) >= 2:
                if self.ver_pattern.match(parts[1]):
                    self.pkg_version.add(parts[1])
                elif parts[1].endswith(".zip"):
                    self.pkg_version.add(parts[1][:-4])
                elif parts[1].endswith(".tar.gz"):
                    self.pkg_version.add(parts[1][:-7])


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


def get_latest_pypi_package_version_from_artifactory(pkg_name, display_all=False, base_version: str = None):
    """
    Utility to get the latest version for a given package name
    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
        base_version: Base version
    Returns: the latest version of ven package
    """
    pkg_url = "/".join([PYPI_PRODUCTION_SIMPLE, pkg_name])
    return get_latest_version_from_site(pkg_url, display_all=display_all, base_version=base_version)


def get_pypi_package_versions_from_artifactory(pkg_name, display_all=False, base_version: str = None, exclude_pre_release: bool = True):
    """
    Utility to get versions of a package in artifactory

    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
        base_version: Base version
        exclude_pre_release: Exclude any prerelease versions

    Returns: the latest version of ven package
    """
    pkg_url = "/".join([PYPI_PRODUCTION_SIMPLE, pkg_name])
    return get_versions_from_site(pkg_url, base_version, display_all=display_all, parser=LinkNameParser, exclude_pre_release=exclude_pre_release)


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
    pkg_url = "/".join([pkg_path, pkg_name])
    base_version = ".".join(base_version.replace("+nightly", "").split(".")[:2])
    return get_latest_version_from_site(pkg_url, base_version=base_version, display_all=display_all, parser=LinkHTMLParser)


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
def fetch_versions_from_server(pkg_url: str, parser: Type[PackageHTMLParser] = LinkHTMLParser) -> List[str]:
    """
    Fetch all versions from server

    Args:
        pkg_url: Url to fetch
        parser: Parser tp use
    Returns:

    """
    resp = requests.get(pkg_url)
    if resp.status_code != 200:
        logger.warning('Could not fetch URL')
        return None

    html_str = resp.text

    parser = parser()
    parser.feed(html_str)
    releases = parser.pkg_version
    releases = [v for v in releases if not v.startswith('.')]

    all_releases = sorted(releases, key=parse_version, reverse=True)
    return all_releases


@functools.lru_cache(3)
def get_versions_from_site(pkg_url, base_version: Optional[str] = None, display_all=False, parser: Type[PackageHTMLParser] = LinkNameParser, exclude_pre_release: bool = True):
    """
    Utility to get the the available versions for a package. The default properties filter out pre releases. You can also include a base version to only list items starting with a particular version

    Args:
        pkg_url: package name given
        base_version: Optional base version. Versions above this will not be added. For example, to get versions 1.18.5, 1.18.4, 1.18.3, 1.18.2 pass 1.18
        display_all: determine if output all package releases
        parser: Parser needs to be a HTMLParser that returns a pkg_versions
        exclude_pre_release: Exclude prerelease versions

    Returns: the latest version of ven package
    """
    all_releases = fetch_versions_from_server(pkg_url, parser=parser)
    if all_releases is None:
        raise ValueError(f"Could not determine latest version for package {pkg_url}. You can manually specify a version to avoid this error")

    if display_all:
        print(all_releases)
    if exclude_pre_release:
        ver_pattern = re.compile(r'^[\d\.]+$')
        release_versions = [ver for ver in all_releases if ver_pattern.match(ver)]
    else:
        release_versions = all_releases

    if base_version:
        release_versions = [ver for ver in release_versions if ver.startswith(base_version)]

    # comps_ssmt_worker will store only x.x.x.x
    if 'comps_ssmt_worker' in pkg_url.lower():
        release_versions = [ver for ver in release_versions if len(ver.split('.')) == 4]
    return release_versions


@functools.lru_cache(3)
def get_latest_version_from_site(pkg_url, base_version: Optional[str] = None, display_all=False, parser: Type[PackageHTMLParser] = LinkNameParser, exclude_pre_release: bool = True):
    """
    Utility to get the latest version for a given package name

    Args:
        pkg_url: package name given
        base_version: Optional base version. Versions above this will not be added.
        display_all: determine if output all package releases
        parser: Parser needs to be a HTMLParser that returns a pkg_versions
        exclude_pre_release: Exclude pre-release versions

    Returns: the latest version of ven package
    """
    if logger.isEnabledFor(DEBUG):
        logger.debug(f"Fetching version from {pkg_url} with base {base_version}")
    release_versions = get_versions_from_site(pkg_url, base_version, display_all=display_all, parser=parser, exclude_pre_release=exclude_pre_release)
    if base_version:
        if logger.isEnabledFor(DEBUG):
            logger.debug(f"Finding latest of matches for version {base_version} from {release_versions}")
        # only use the longest match latest
        version_compatible_portion = ".".join(base_version.split(".")[:2])

        for ver in release_versions:
            if ".".join(ver.split('.')[:2]) == version_compatible_portion:
                return ver
        return None
    return release_versions[0] if release_versions else None
