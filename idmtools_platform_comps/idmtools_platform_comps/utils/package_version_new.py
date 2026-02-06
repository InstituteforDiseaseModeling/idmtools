"""idmtools Tools to filter versions of packages for requirements for asset collections.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import functools
import os
import re
from logging import getLogger
from typing import Optional, List, Dict
import requests
from packaging.requirements import Requirement
from packaging.version import Version, parse

user_logger = getLogger('user')
logger = getLogger(__name__)

PKG_PYPI = 'https://pypi.org/pypi/{}/json'
GHCR_ORG = 'institutefordiseasemodeling'  # Default organization name
#GHCR_ORG = 'shchen-idmod'  # Default organization name
GHCR_IMAGE = 'idmtools-comps-ssmt-worker'
GHCR_PRODUCTION = f"ghcr.io/{GHCR_ORG}/{GHCR_IMAGE}"
GHCR_STAGING = f"ghcr.io/{GHCR_ORG}/{GHCR_IMAGE}-staging"
MANIFEST_URL = "https://hub.docker.com/v2/repositories/library/{repository}/tags/?page_size=25&page=1&name={tag}"


def get_latest_package_version_from_pypi(pkg_name, display_all=False):
    """
    Utility to get the latest version for a given package name from PyPI.

    Args:
        pkg_name: package name given
        display_all: determine if output all package releases

    Returns: the latest version of given package
    """
    url = PKG_PYPI.format(pkg_name)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        releases = response.json()['releases']
    except Exception as e:
        logger.warning(f"Failed to fetch package '{pkg_name}' from PyPI: {e}")
        return None

    all_releases = sorted(releases, key=parse, reverse=True)

    if display_all:
        print(all_releases)

    release_versions = [ver for ver in all_releases if not parse(ver).is_prerelease]

    if not release_versions:
        return None

    return release_versions[0]


@functools.lru_cache(maxsize=128)
def fetch_docker_tags_from_ghcr(image_name: str, org: str = GHCR_ORG, token: Optional[str] = None) -> List[str]:
    """
    Fetch all tags for a Docker image from GitHub Container Registry.

    Args:
        image_name: Image name (e.g., 'idmtools-comps-ssmt-worker')
        org: Organization name (default: institutefordiseasemodeling)
        token: Optional GitHub Personal Access Token for private images

    Returns:
        List of version tags, sorted from newest to oldest

    Examples:
        >>> fetch_docker_tags_from_ghcr('idmtools-comps-ssmt-worker')
        ['1.0.0.3', '1.0.0.2', '1.0.0.1', 'latest']
    """
    url = f"https://ghcr.io/v2/{org}/{image_name}/tags/list"
    headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        response = requests.get(url, headers=headers, timeout=10)

        # Get anonymous token if 401
        if response.status_code == 401 and not token:
            auth_url = f"https://ghcr.io/token?scope=repository:{org}/{image_name}:pull"
            auth_response = requests.get(auth_url, timeout=10)

            if auth_response.ok:
                token_data = auth_response.json()
                headers['Authorization'] = f"Bearer {token_data.get('token', '')}"
                response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            tags = data.get('tags', [])

            # Separate version tags from special tags
            version_tags = [t for t in tags if t not in ['latest', 'dev', 'main', 'master']]

            # Sort by version
            try:
                sorted_tags = sorted(version_tags, key=parse, reverse=True)
                # Add back 'latest' at the end if it exists
                if 'latest' in tags:
                    sorted_tags.append('latest')
                return sorted_tags
            except Exception:
                return tags
        else:
            logger.warning(f"Failed to fetch tags for {org}/{image_name}: HTTP {response.status_code}")
            return []

    except requests.RequestException as e:
        logger.error(f"Error fetching GHCR tags for {org}/{image_name}: {e}")
        return []


def get_latest_docker_image_version_from_ghcr(
        image_name: str,
        base_version: Optional[str] = None,
        display_all: bool = False,
        org: str = GHCR_ORG,
        token: Optional[str] = None
) -> Optional[str]:
    """
    Get the latest version for a Docker image from GitHub Container Registry.

    Args:
        image_name: Image name (e.g., 'idmtools-comps-ssmt-worker')
        base_version: Optional base version. Only versions matching this prefix will be considered.
        display_all: If True, print all available versions
        org: Organization name
        token: Optional GitHub PAT for private images

    Returns:
        Latest matching version string, or None if not found

    Examples:
        >>> get_latest_docker_image_version_from_ghcr('idmtools-comps-ssmt-worker')
        '1.0.0.3'

        >>> get_latest_docker_image_version_from_ghcr('idmtools-comps-ssmt-worker', base_version='1.0.0')
        '1.0.0.3'
    """
    versions = fetch_docker_tags_from_ghcr(image_name, org=org, token=token)

    if not versions:
        logger.warning(f"No versions found for {org}/{image_name}")
        return None

    # Filter out non-version tags
    version_pattern = re.compile(r'^\d+\.\d+\.\d+(\.\d+)?$')
    version_tags = [v for v in versions if version_pattern.match(v)]

    if display_all:
        print(f"Available versions for {image_name}:", version_tags)

    if not version_tags:
        return None

    # If base_version specified, filter matching versions
    if base_version:
        v = parse(base_version)
        new_base_version = v.base_version
        matching = [v for v in version_tags if v.startswith(new_base_version)]
        return matching[0] if matching else None

    return version_tags[0]


def get_ghcr_manifest(repository: str, tag: str, platform: str = "linux/amd64") -> dict:
    """
    Get the manifest from GitHub Container Registry.
    Handles both direct manifests and manifest lists (multi-platform images).

    Args:
        repository: Repository path (e.g., "username/imagename")
        tag: Image tag (e.g., "latest", "v1.0")
        platform: Platform string like "linux/amd64" or "linux/arm64"

    Returns:
        Full manifest dictionary with config
    """
    import requests

    url = f"https://ghcr.io/v2/{repository}/manifests/{tag}"

    headers = {
        # Accept both OCI and Docker v2 formats
        "Accept": ", ".join([
            "application/vnd.oci.image.index.v1+json",
            "application/vnd.oci.image.manifest.v1+json",
            "application/vnd.docker.distribution.manifest.v2+json",
            "application/vnd.docker.distribution.manifest.list.v2+json"
        ])
    }

    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    manifest = response.json()

    # Check if this is a manifest list/index (multi-platform)
    media_type = manifest.get("mediaType", "")
    if "index" in media_type or "manifest.list" in media_type:
        # Parse platform (e.g., "linux/amd64" -> os="linux", arch="amd64")
        os_name, arch = platform.split("/") if "/" in platform else ("linux", platform)

        # Find the matching platform manifest
        platform_manifest = None
        for m in manifest.get("manifests", []):
            p = m.get("platform", {})
            if p.get("os") == os_name and p.get("architecture") == arch:
                platform_manifest = m
                break

        if not platform_manifest:
            # Fallback: use first manifest if platform not found
            print(f"Warning: Platform {platform} not found, using first available manifest")
            platform_manifest = manifest["manifests"][0]

        # Fetch the platform-specific manifest using its digest
        platform_digest = platform_manifest["digest"]
        platform_url = f"https://ghcr.io/v2/{repository}/manifests/{platform_digest}"

        response = requests.get(platform_url, headers=headers)
        response.raise_for_status()
        manifest = response.json()

    # Now we should have the actual manifest with config
    if "config" not in manifest:
        raise ValueError(
            f"Manifest does not contain 'config' field. "
            f"MediaType: {manifest.get('mediaType')}, "
            f"Keys: {list(manifest.keys())}"
        )

    return manifest

def get_ghcr_image_info(
        image_name: str,
        tag: str = 'latest',
        org: str = GHCR_ORG,
        token: Optional[str] = None
) -> Optional[Dict]:
    """
    Get comprehensive information about a GHCR image including platforms and size.

    Args:
        image_name: Image name
        tag: Image tag
        org: Organization or username
        token: Optional GitHub PAT

    Returns:
        Dictionary with image information or None if not found

    Example:
        >>> info = get_ghcr_image_info('idmtools-comps-ssmt-worker', '1.0.0.3')
        >>> print(f"Platforms: {info['platforms']}")
        >>> print(f"Size: {info['total_size_mb']:.2f} MB")
    """
    manifest = get_ghcr_manifest(image_name, tag, org, token)

    if not manifest:
        return None

    info = {
        'image': f"{org}/{image_name}:{tag}",
        'media_type': manifest.get('mediaType'),
        'schema_version': manifest.get('schemaVersion'),
        'platforms': [],
        'manifests': [],
        'total_size_mb': 0
    }

    # Handle OCI index / manifest list (multi-platform)
    if 'manifests' in manifest:
        for m in manifest['manifests']:
            platform_info = m.get('platform', {})
            arch = platform_info.get('architecture', 'unknown')
            os_name = platform_info.get('os', 'unknown')
            variant = platform_info.get('variant', '')

            platform_str = f"{os_name}/{arch}"
            if variant:
                platform_str += f"/{variant}"

            info['platforms'].append(platform_str)
            info['manifests'].append({
                'digest': m.get('digest'),
                'size': m.get('size', 0),
                'platform': platform_str
            })

            info['total_size_mb'] += m.get('size', 0) / 1024 / 1024

    # Handle single-platform manifest
    elif 'layers' in manifest:
        layers = manifest.get('layers', [])
        total_size = sum(layer.get('size', 0) for layer in layers)
        info['total_size_mb'] = total_size / 1024 / 1024
        info['layer_count'] = len(layers)

        if 'config' in manifest:
            info['config_digest'] = manifest['config'].get('digest')

    return info


def check_ghcr_image_exists(
        image_name: str,
        org: str = GHCR_ORG,
        token: Optional[str] = None
) -> Dict[str, any]:
    """
    Check if a GHCR image exists and return diagnostic information.

    Args:
        image_name: Image name
        org: Organization or username
        token: Optional GitHub PAT

    Returns:
        Dictionary with diagnostic info:
        - exists: bool
        - tags: list of available tags (if exists)
        - url: URL to check in browser
        - error: error message (if any)
    """
    result = {
        'exists': False,
        'tags': [],
        'url': f'https://github.com/{org}/pkgs/container/{image_name}',
        'error': None
    }

    tags_url = f"https://ghcr.io/v2/{org}/{image_name}/tags/list"
    headers = {}

    if token:
        headers['Authorization'] = f'Bearer {token}'

    try:
        response = requests.get(tags_url, headers=headers, timeout=10)

        # Try to get anonymous token if 401
        if response.status_code == 401 and not token:
            auth_url = f"https://ghcr.io/token?scope=repository:{org}/{image_name}:pull"
            auth_response = requests.get(auth_url, timeout=10)

            if auth_response.ok:
                token_data = auth_response.json()
                headers['Authorization'] = f"Bearer {token_data.get('token', '')}"
                response = requests.get(tags_url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            result['exists'] = True
            result['tags'] = data.get('tags', [])
        elif response.status_code == 404:
            result['error'] = f"Image not found at {org}/{image_name}"
        elif response.status_code == 401:
            result['error'] = "Authentication failed - image may be private"
        else:
            result['error'] = f"HTTP {response.status_code}"

    except Exception as e:
        result['error'] = str(e)

    return result


def get_digest_from_docker_hub(repo, tag='latest'):
    """
    Get the digest for image from docker hub.

    Args:
        repo: string, repository (e.g. 'library/fedora')
        tag: string, tag of the repository (e.g. 'latest')

    Returns:
        Digest string or None if not found
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


@functools.lru_cache(maxsize=128)
def fetch_package_versions_from_pypi(pkg_name: str, include_prereleases: bool = False) -> List[str]:
    """
    Fetch all available versions of a package from PyPI.

    Args:
        pkg_name: Package name on PyPI
        include_prereleases: If True, include pre-release versions

    Returns:
        List of version strings, sorted from newest to oldest
    """
    url = PKG_PYPI.format(pkg_name)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        releases = response.json()['releases']
    except requests.RequestException as e:
        logger.error(f"Failed to fetch versions for '{pkg_name}' from PyPI: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing PyPI response for '{pkg_name}': {e}")
        return []

    versions = list(releases.keys())

    # Filter out pre-releases if requested
    if not include_prereleases:
        versions = [v for v in versions if not parse(v).is_prerelease]

    # Sort versions from newest to oldest
    sorted_versions = sorted(versions, key=parse, reverse=True)

    return sorted_versions


def fetch_package_versions(pkg_name, is_released=True, sort=True, display_all=False, source='pypi', **kwargs):
    """
    Utility to get versions for a given package name.

    Supports multiple sources: PyPI and GHCR (for Docker images).

    Args:
        pkg_name: package name given (e.g., 'idmtools' for PyPI or 'idmtools-comps-ssmt-worker' for Docker)
        is_released: get released version only (filters pre-releases)
        sort: make version sorted or not
        display_all: determine if output all package releases
        source: Source to fetch from ('pypi', 'ghcr')
        **kwargs: Additional arguments (e.g., org, token for GHCR)

    Returns: list of versions of given package

    Examples:
        >>> fetch_package_versions('idmtools')  # PyPI
        ['3.0.2', '3.0.1', '3.0.0']

        >>> fetch_package_versions('idmtools-comps-ssmt-worker', source='ghcr')
        ['1.0.0.3', '1.0.0.2', '1.0.0.1']
    """
    versions = []

    # GHCR source (for Docker images)
    if source == 'ghcr':
        versions = fetch_docker_tags_from_ghcr(
            pkg_name,
            org=kwargs.get('org', GHCR_ORG),
            token=kwargs.get('token')
        )
        # Filter out non-version tags like 'latest', 'dev', etc.
        if is_released:
            version_pattern = re.compile(r'^\d+\.\d+\.\d+(\.\d+)?$')
            versions = [v for v in versions if version_pattern.match(v)]

    # PyPI source (default)
    else:
        versions = fetch_package_versions_from_pypi(pkg_name, include_prereleases=not is_released)

    if sort and versions:
        try:
            versions = sorted(versions, key=parse, reverse=True)
        except Exception as e:
            logger.warning(f"Could not sort versions for {pkg_name}: {e}")

    if display_all:
        print(f"Available versions for {pkg_name} (source: {source}):", versions)

    return versions


def get_highest_version(pkg_requirement: str):
    """
    Utility to get the highest version that satisfies a package requirement.

    Args:
        pkg_requirement: package requirement string (e.g., "requests>=2.0,<3.0")

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

    Raises:
        SystemExit if no valid versions found
    """
    version = get_highest_version(pkg_name)
    if version is None:
        user_logger.info(f"No valid versions found for '{pkg_name}'")
        exit(1)
    return version


def get_latest_compatible_version(pkg_name, base_version=None, versions=None, validate=True):
    """
    Utility to get the latest compatible version from a given version list or PyPI.

    Args:
        pkg_name: package name
        base_version: Optional base version. Only versions matching this prefix will be considered.
        versions: Optional user-provided version list. If None, fetches from PyPI.
        validate: If True, validates that base_version exists in the version list

    Returns: the latest compatible version string, or None if not found

    Examples:
        >>> get_latest_compatible_version("requests")
        '2.31.0'

        >>> get_latest_compatible_version("requests", base_version="2.28")
        '2.28.2'

        >>> get_latest_compatible_version("requests", base_version="2.28.1")
        '2.28.1'
    """
    # Fetch versions if not provided
    if versions is None:
        versions = fetch_package_versions(pkg_name)

    # Return None if version list is empty
    if not versions:
        user_logger.warning(f"No versions found for package '{pkg_name}'")
        return None

    # Return the latest version if no base_version is given
    if base_version is None:
        return versions[0]

    # Cleanup base_version
    base_version = base_version.replace('+nightly', '').strip()

    # Parse and validate the base version
    try:
        parsed_version_to_check = parse(base_version)
    except Exception as e:
        user_logger.error(f"Invalid version format '{base_version}': {e}")
        return None

    # Check if the exact version exists in the list
    is_in_list = any(parsed_version_to_check == parse(version) for version in versions)
    if not is_in_list and validate:
        user_logger.info(f"Could not find the version '{base_version}' for '{pkg_name}'.")
        return None

    # Find all candidates that match the base version prefix
    candidates = [version for version in versions if version.startswith(base_version)]

    # Return the latest matching candidate
    if candidates:
        return candidates[0]

    user_logger.info(f"No versions matching '{base_version}' found for '{pkg_name}'.")
    return None


def get_next_docker_image_version_from_ghcr() -> str:
    """
    Returns the next recommended version, incrementing the build number
    of the latest matching BASE_VERSION tag.
    """
    from idmtools_platform_comps import __version__

    current = get_latest_docker_image_version_from_ghcr(GHCR_IMAGE, base_version=__version__)

    if current is None:
        # No existing version found - use first 3 parts of __version__ with .0
        v = parse(__version__)
        next_version = f"{v.base_version}.0"
    else:
        # Parse existing version
        parts = current.split(".")
        base = ".".join(parts[:3])
        build = int(parts[3]) if len(parts) == 4 else 0

        # Safety check: compare with current __version__
        v = parse(__version__)
        new_base_version = v.base_version

        if base != new_base_version:
            print(f"Warning: current base {base} != expected {new_base_version} → resetting")
            next_version = f"{new_base_version}.0"
        else:
            next_version = f"{new_base_version}.{build + 1}"

    user_logger.info(f"Next version: {current} → {next_version}")
    return next_version
