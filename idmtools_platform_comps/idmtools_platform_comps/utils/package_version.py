"""idmtools Tools to filter versions of packages for requriements for asset collections.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import functools
import operator
import json
import os
import re
from abc import ABC
from datetime import datetime
from logging import getLogger, DEBUG
from typing import Optional, List, Type, Dict, Tuple
from urllib import request
import requests
from packaging.requirements import Requirement
from packaging.version import Version, parse
from html.parser import HTMLParser

user_logger = getLogger('user')


PKG_PYPI = 'https://pypi.python.org/pypi/{}/json'
PYPI_PRODUCTION_SIMPLE = 'https://packages.idmod.org/artifactory/api/pypi/pypi-production/simple'

IDM_DOCKER_PROD = 'https://packages.idmod.org/artifactory/list/docker-production'
IDMTOOLS_DOCKER_PROD = f'{IDM_DOCKER_PROD}/idmtools/'
MANIFEST_URL = "https://hub.docker.com/v2/repositories/library/{repository}/tags/?page_size=25&page=1&name={tag}"

logger = getLogger(__name__)


class PackageHTMLParser(HTMLParser, ABC):
    """Base Parser for our other parsers."""
    previous_tag = None
    pkg_version = None

    def __init__(self):
        """Constructor."""
        super().__init__()
        self.pkg_version = set()


class LinkHTMLParser(PackageHTMLParser):
    """Parse hrefs from links."""

    def handle_starttag(self, tag, attrs):
        """Parse links and extra hrefs."""
        self.previous_tag = tag
        if tag != 'a':
            return

        attr = dict(attrs)
        v = attr['href']
        v = v.rstrip('/')
        self.pkg_version.add(v)


class LinkNameParser(PackageHTMLParser):
    """
    Provides parsing of packages from pypi/arfifactory.

    We parse links that match versions patterns
    """
    in_link = False
    ver_pattern = re.compile(r'^[\d\.brcdev\+nightly]+$')

    def handle_starttag(self, tag, attrs):
        """Handle begin of links."""
        self.previous_tag = tag
        self.in_link = tag == "a"

    def handle_endtag(self, tag):
        """End link tags."""
        if tag == "a":
            self.in_link = False

    def handle_data(self, data):
        """Process links."""
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
    Utility to get the latest version for a given package name.

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

    all_releases = sorted(releases, key=parse, reverse=True)

    if display_all:
        print(all_releases)

    release_versions = [ver for ver in all_releases if not parse(ver).is_prerelease]
    latest_version = release_versions[0]

    return latest_version


def get_latest_pypi_package_version_from_artifactory(pkg_name, display_all=False, base_version: str = None):
    """
    Utility to get the latest version for a given package name.

    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
        base_version: Base version

    Returns: the latest version of ven package
    """
    pkg_url = "/".join([PYPI_PRODUCTION_SIMPLE, pkg_name])
    return get_latest_version_from_site(pkg_url, display_all=display_all, base_version=base_version)


def get_pypi_package_versions_from_artifactory(pkg_name, display_all=False, base_version: str = None,
                                               exclude_pre_release: bool = True):
    """
    Utility to get versions of a package in artifactory.

    Args:
        pkg_name: package name given
        display_all: determine if output all package releases
        base_version: Base version
        exclude_pre_release: Exclude any prerelease versions

    Returns: the latest version of ven package
    """
    pkg_url = "/".join([PYPI_PRODUCTION_SIMPLE, pkg_name])
    return get_versions_from_site(pkg_url, base_version, display_all=display_all, parser=LinkNameParser,
                                  exclude_pre_release=exclude_pre_release)


def get_latest_ssmt_image_version_from_artifactory(pkg_name='comps_ssmt_worker', base_version: Optional[str] = None,
                                                   display_all=False):
    """
    Utility to get the latest version for a given package name.

    Args:
        pkg_name: package name given
        base_version: Optional base version. Versions above this will not be added.
        display_all: determine if output all package releases

    Returns: the latest version of ven package
    """
    pkg_path = IDMTOOLS_DOCKER_PROD
    pkg_url = "/".join([pkg_path, pkg_name])
    base_version = ".".join(base_version.replace("+nightly", "").split(".")[:2])
    return get_latest_version_from_site(pkg_url, base_version=base_version, display_all=display_all,
                                        parser=LinkHTMLParser)


def get_docker_manifest(
        image_path: str = "library/ubuntu",
        tag: str = "latest",
        registry: str = "registry-1.docker.io",
        token: Optional[str] = None
) -> Optional[Tuple[Dict, str]]:
    """
    Get Docker manifest from Docker Hub.
    Handles both official images (library/*) and user/org images.

    Args:
        image_path: Image path (e.g., 'library/ubuntu' or 'username/image')
        tag: Image tag (default: 'latest')
        registry: Docker registry URL (default: Docker Hub)
        token: Optional Docker Hub auth token

    Returns:
        Tuple of (manifest dict, full image path with tag) or None if not found

    Examples:
        >>> manifest, path = get_docker_manifest('library/ubuntu', 'latest')
        >>> manifest, path = get_docker_manifest('username/myimage', '1.0.0')

    Raises:
        ValueError: When the manifest cannot be found
    """
    try:
        # Parse image path - handle both "image:tag" and separate args
        if ":" in image_path:
            image_path, tag = image_path.split(":", 1)

        # Normalize image path for Docker Hub
        # Official images need 'library/' prefix
        if '/' not in image_path:
            image_path = f'library/{image_path}'

        # Get authentication token
        auth_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{image_path}:pull"
        auth_headers = {}

        if token:
            # If user provided Docker Hub token
            auth_headers['Authorization'] = f'Bearer {token}'

        auth_response = requests.get(auth_url, headers=auth_headers, timeout=10)

        if not auth_response.ok:
            logger.warning(f"Failed to get token for {image_path}")
            raise ValueError(f"Failed to authenticate with Docker Hub for {image_path}")

        bearer_token = auth_response.json().get('token', '')
        if not bearer_token:
            logger.warning(f"No token returned for {image_path}")
            raise ValueError(f"No authentication token received for {image_path}")

        # Fetch manifest
        manifest_url = f"https://{registry}/v2/{image_path}/manifests/{tag}"

        # Accept multiple manifest formats
        accept_formats = [
            'application/vnd.oci.image.index.v1+json',
            'application/vnd.docker.distribution.manifest.list.v2+json',
            'application/vnd.oci.image.manifest.v1+json',
            'application/vnd.docker.distribution.manifest.v2+json',
        ]

        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Accept': ', '.join(accept_formats)
        }

        response = requests.get(manifest_url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise ValueError(f"Could not find manifest for {image_path}:{tag} (status: {response.status_code})")

        manifest = response.json()
        media_type = manifest.get('mediaType', '')

        # Handle manifest lists (multi-platform images)
        if 'index' in media_type or 'manifest.list' in media_type:
            logger.info(f"Found multi-platform image for {image_path}:{tag}")
            manifest = _extract_platform_manifest_dockerhub(
                manifest,
                'linux/amd64',  # Default platform
                registry,
                image_path,
                bearer_token
            )

            if not manifest:
                raise ValueError(f"Could not extract platform manifest for {image_path}:{tag}")

        full_image_path = f"{image_path}:{tag}"
        return manifest, full_image_path

    except requests.RequestException as e:
        logger.error(f"Error fetching Docker Hub manifest: {e}")
        raise ValueError(f"Network error fetching manifest for {image_path}:{tag}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise ValueError(f"Error fetching manifest for {image_path}:{tag}: {e}")


def _extract_platform_manifest_dockerhub(
        manifest_list: Dict,
        platform: str,
        registry: str,
        image_path: str,
        bearer_token: str
) -> Optional[Dict]:
    """
    Extract platform-specific manifest from Docker Hub manifest list.

    Args:
        manifest_list: The manifest list/index
        platform: Target platform (e.g., 'linux/amd64')
        registry: Docker registry URL
        image_path: Image path
        bearer_token: Authentication token

    Returns:
        Platform-specific manifest or None
    """
    try:
        # Parse platform
        if '/' in platform:
            os_name, arch = platform.split('/', 1)
        else:
            os_name, arch = 'linux', platform

        # Find matching platform
        manifests = manifest_list.get('manifests', [])
        platform_manifest = None

        for m in manifests:
            p = m.get('platform', {})
            if p.get('os') == os_name and p.get('architecture') == arch:
                platform_manifest = m
                break

        if not platform_manifest:
            logger.warning(f"Platform {platform} not found, using first available")
            platform_manifest = manifests[0] if manifests else None

        if not platform_manifest:
            logger.error("No manifests found in manifest list")
            return None

        # Fetch platform-specific manifest
        digest = platform_manifest['digest']
        platform_url = f"https://{registry}/v2/{image_path}/manifests/{digest}"

        headers = {
            'Authorization': f'Bearer {bearer_token}',
            'Accept': ', '.join([
                'application/vnd.oci.image.manifest.v1+json',
                'application/vnd.docker.distribution.manifest.v2+json',
            ])
        }

        response = requests.get(platform_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to fetch platform manifest: {response.status_code}")
            return None

    except Exception as e:
        logger.error(f"Error extracting platform manifest: {e}")
        return None


def get_latest_tag_dockerhub(image_path: str) -> str:
    """
    Get the latest tag for a Docker Hub image by checking available tags.

    Args:
        image_path: Image path (e.g., 'library/ubuntu' or 'username/image')

    Returns:
        Latest tag name

    Examples:
        >>> tag = get_latest_tag_dockerhub('library/ubuntu')
    """
    try:
        # Normalize path
        if '/' not in image_path:
            image_path = f'library/{image_path}'

        # Get auth token
        auth_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{image_path}:pull"
        auth_response = requests.get(auth_url, timeout=10)

        if not auth_response.ok:
            return 'latest'

        bearer_token = auth_response.json().get('token', '')

        # List tags
        tags_url = f"https://registry-1.docker.io/v2/{image_path}/tags/list"
        headers = {'Authorization': f'Bearer {bearer_token}'}

        response = requests.get(tags_url, headers=headers, timeout=10)

        if response.status_code == 200:
            tags = response.json().get('tags', [])

            # Filter out 'latest' and sort
            version_tags = [t for t in tags if t != 'latest' and not any(x in t for x in ['dev', 'test', 'rc'])]

            if version_tags:
                # Try to sort by version
                try:
                    from packaging.version import parse, InvalidVersion
                    sorted_tags = sorted(version_tags, key=lambda x: parse(x) if x[0].isdigit() else x, reverse=True)
                    return sorted_tags[0]
                except (ImportError, InvalidVersion):
                    # Fallback to alphabetical
                    return sorted(version_tags, reverse=True)[0]

        return 'latest'

    except Exception as e:
        logger.warning(f"Could not determine latest tag: {e}")
        return 'latest'

def get_digest_from_docker_hub(repo, tag='latest'):
    """
    Get the digest for image from docker.

    Args:
        repo: string, repository (e.g. 'library/fedora')
        tag:  string, tag of the repository (e.g. 'latest')
    """
    response = requests.get(
        MANIFEST_URL.format(repository=repo, tag=tag)
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
    Fetch all versions from server.

    Args:
        pkg_url: Url to fetch
        parser: Parser tp use

    Returns:
        All the releases for a package
    """
    resp = requests.get(pkg_url)
    pkg_name = pkg_url.split('/')[-1]
    if resp.status_code != 200:
        logger.warning(f"Error fetching package {pkg_name} information. Status code: {resp.status_code}")
        return []

    html_str = resp.text

    parser = parser()
    parser.feed(html_str)
    releases = parser.pkg_version
    releases = [v for v in releases if not v.startswith('.')]

    all_releases = sorted(releases, key=parse, reverse=True)
    return all_releases


def fetch_versions_from_artifactory(pkg_name: str, parser: Type[PackageHTMLParser] = LinkHTMLParser) -> List[str]:
    """
    Fetch all versions from server.

    Args:
        pkg_name: Url to fetch
        parser: Parser tp use

    Returns:
        Available releases
    """
    pkg_path = IDM_DOCKER_PROD
    pkg_url = os.path.join(pkg_path, pkg_name)

    resp = requests.get(pkg_url)
    if resp.status_code != 200:
        logger.warning('Could not fetch URL')
        return None

    html_str = resp.text

    parser = parser()
    parser.feed(html_str)
    releases = parser.pkg_version
    releases = [v for v in releases if not v.startswith('.')]

    all_releases = sorted(releases, key=parse, reverse=True)
    return all_releases


@functools.lru_cache(3)
def get_versions_from_site(pkg_url, base_version: Optional[str] = None, display_all=False,
                           parser: Type[PackageHTMLParser] = LinkNameParser, exclude_pre_release: bool = True):
    """
    Utility to get the the available versions for a package.

    The default properties filter out pre releases. You can also include a base version to only list items starting with a particular version

    Args:
        pkg_url: package name given
        base_version: Optional base version. Versions above this will not be added. For example, to get versions 1.18.5, 1.18.4, 1.18.3, 1.18.2 pass 1.18
        display_all: determine if output all package releases
        parser: Parser needs to be a HTMLParser that returns a pkg_versions
        exclude_pre_release: Exclude prerelease versions

    Returns: the latest version of ven package

    Raises:
        ValueError - If a latest versions cannot be determined
    """
    all_releases = fetch_versions_from_server(pkg_url, parser=parser)
    if all_releases is None:
        raise ValueError(
            f"Could not determine latest version for package {pkg_url}. You can manually specify a version to avoid this error")

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
def get_latest_version_from_site(pkg_url, base_version: Optional[str] = None, display_all=False,
                                 parser: Type[PackageHTMLParser] = LinkNameParser, exclude_pre_release: bool = True):
    """
    Utility to get the latest version for a given package name.

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
    release_versions = get_versions_from_site(pkg_url, base_version, display_all=display_all, parser=parser,
                                              exclude_pre_release=exclude_pre_release)
    if base_version:
        # only use the longest match latest
        version_compatible_portion = ".".join(base_version.split(".")[:2])
        if logger.isEnabledFor(DEBUG):
            logger.debug(
                f"Finding latest of matches for version {base_version} from {release_versions} using {version_compatible_portion}")

        for ver in release_versions:
            if ".".join(ver.split('.')[:2]) == version_compatible_portion:
                return ver
        return None
    return release_versions[0] if release_versions else None


def fetch_package_versions_from_pypi(pkg_name):
    """
    Utility to get the latest version for a given package name.

    Args:
        pkg_name: package name given

    Returns: the latest version of ven package
    """
    url = PKG_PYPI.format(pkg_name)
    try:
        releases = json.loads(request.urlopen(url).read())['releases']
    except Exception:
        return None

    return releases


def fetch_package_versions(pkg_name, is_released=True, sort=True, display_all=False):
    """
    Utility to get the latest version for a given package name.

    Args:
        pkg_name: package name given
        is_released: get released version only
        sort: make version sorted or not
        display_all: determine if output all package releases

    Returns: the latest version of ven package
    """
    # First fetch versions from Artifactory
    pkg_url = "/".join([PYPI_PRODUCTION_SIMPLE, pkg_name])
    versions = fetch_versions_from_server(pkg_url, parser=LinkNameParser)

    if versions is None:
        versions = fetch_package_versions_from_pypi(pkg_name)

    if sort:
        versions = sorted(versions, key=parse, reverse=True)

    if is_released:
        versions = [ver for ver in versions if not parse(ver).is_prerelease]

    if display_all:
        print(display_all)

    return versions


def get_highest_version(pkg_requirement: str):
    """
    Utility to get the latest version for a given package name.

    Args:
        pkg_requirement: package requirement given
    Returns: the highest valid version of the package
    """
    req = Requirement(pkg_requirement)
    available_versions = fetch_package_versions(req.name)

    # Filter versions that satisfy the specifier
    valid_versions = [Version(version) for version in available_versions if parse(version) in req.specifier]

    if not valid_versions:
        return None  # No valid versions found

    # Return the highest valid version
    return str(max(valid_versions))


def get_latest_version(pkg_name):
    """
    Utility to get the latest version for a given package name.

    Args:
        pkg_name: package name given

    Returns: the latest version of package
    """
    version = get_highest_version(pkg_name)
    if version is None:
        user_logger.info(f"No valid versions found for '{pkg_name}'")
        exit(1)
    return version


def get_latest_compatible_version(pkg_name, base_version=None, versions=None, validate=True):
    """
    Utility to get the latest compatible version from a given version list.

    Args:
        base_version: Optional base version. Versions above this will not be added.
        pkg_name: package name given
        versions: user input of version list
        validate: bool, if True, will validate base_version

    Returns: the latest compatible version from versions

    Raises:
        Exception - If we cannot find version
    Notes:
        - TODO - Make custom exception or use ValueError
    """
    if versions is None:
        versions = fetch_package_versions(pkg_name)

    # Return None if given version list is None or empty
    if not versions:
        return None

    # Return the latest version if no base_version is given
    if base_version is None:
        return versions[0]

    # Cleanup
    base_version = base_version.replace('+nightly', '')

    # Make sure the input is valid
    parsed_version_to_check = parse(base_version)

    # Check if the version is in the list
    is_in_list = any(parsed_version_to_check == parse(version) for version in versions)
    if not is_in_list and validate:
        user_logger.info(f"Could not find the version of '{base_version}' for '{pkg_name}'.")
        return None

    # Find all possible candidates
    candidates = [version for version in versions if version.startswith(base_version)]

    # Pick the latest
    return candidates[0]
