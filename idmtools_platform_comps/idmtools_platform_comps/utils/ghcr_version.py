"""
GHCR SSMT image version utilities

Queries GitHub Container Registry to find the current (latest) version
and compute the next logical version for building a new image.

Usage:
    from ghcr_ssmt_version import get_current_ssmt_image_version, get_next_ssmt_image_version

    current = get_current_ssmt_image_version(use_production=False)
    next_ver = get_next_ssmt_image_version(use_production=True)
"""

import os
import requests
from typing import Optional, Tuple
from natsort import natsorted

# Adjust these to match your actual repositories
GHCR_PRODUCTION = "ghcr.io/shchen-idmod/idmtools-comps-ssmt-worker"
GHCR_STAGING    = "ghcr.io/shchen-idmod/idmtools-comps-ssmt-worker-staging"
# GHCR_PRODUCTION = 'ghcr.io/institutefordiseasemodeling/idmtools-comps-ssmt-worker'
# GHCR_STAGING = 'ghcr.io/institutefordiseasemodeling/idmtools-comps-ssmt-worker-staging'

DOCKER_HUB_PRODUCTION = 'shchen-idmod/idmtools-comps-ssmt-worker'
DOCKER_HUB_STAGING = 'shchen-idmod/idmtools-comps-ssmt-worker-staging'

# Read BASE_VERSION from your repo's VERSION file (adjust path if needed)
try:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_VERSION = open(os.path.join(BASE_DIR, "..", "VERSION")).read().strip()
except Exception:
    BASE_VERSION = "0.0.0"  # fallback


def _get_github_token() -> Optional[str]:
    """Look for common GitHub token environment variables."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def _fetch_latest_tag(image: str, token: Optional[str] = None) -> Optional[str]:
    """Internal: Get the highest sorted 4-part version tag from GHCR."""
    if not image.startswith("ghcr.io/"):
        raise ValueError(f"Expected GHCR image format: {image}")

    #path = image.replace("ghcr.io/", "").rstrip("/")
    path = image.replace("ghcr.io/", "")
    org_repo = path.rstrip("/")

    url = f"https://ghcr.io/v2/{org_repo}/tags/list"
    token_url = "https://ghcr.io/token"
    params = {
        "service": "ghcr.io",
        "scope": f"repository:{org_repo}:pull",
    }

    tok = requests.get(token_url, params=params).json()["token"]
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {tok}"})

        if resp.status_code != 200:
            print(f"GHCR tags request failed ({resp.status_code}) for {image}")
            return None

        data = resp.json()
        tags = data.get("tags", []) or []

    except Exception as e:
        print(f"Could not reach GHCR for {image}: {e}")
        return None

    if not tags:
        return None

    # Keep only plausible 4-part versions: x.y.z.b
    valid_tags = [
        t for t in tags
        if len(t.split(".")) == 4 and all(p.isdigit() for p in t.split("."))
    ]

    if not valid_tags:
        return None

    # Natural sort → highest version first
    sorted_tags = natsorted(valid_tags, reverse=True)
    return sorted_tags[0]


def _parse_version(tag: str) -> Tuple[str, int]:
    """Split tag into base (x.y.z) and build number (b)"""
    parts = tag.split(".")
    base = ".".join(parts[:3])
    build = int(parts[3]) if len(parts) == 4 else 0
    return base, build

def _is_valid_version_tag(tag: str) -> bool:
    """Basic check: x.y.z.b where all parts are digits."""
    parts = tag.split(".")
    return len(parts) == 4 and all(p.isdigit() for p in parts)


def _get_base_part(tag: str) -> str:
    """Return x.y.z part of tag."""
    return ".".join(tag.split(".")[:3])

def _fetch_all_tags(image: str, token: Optional[str] = None) -> list:
    """Fetch list of tags from GHCR."""
    if not image.startswith("ghcr.io/"):
        raise ValueError(f"Expected GHCR image format: {image}")

    path = image.replace("ghcr.io/", "").rstrip("/")
    url = f"https://ghcr.io/v2/{path}/tags/list"

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    token_url = "https://ghcr.io/token"
    params = {
        "service": "ghcr.io",
        "scope": f"repository:{path}:pull",
    }

    tok = requests.get(token_url, params=params).json()["token"]
    try:
        r = requests.get(url, headers={"Authorization": f"Bearer {tok}"})

        if r.status_code != 200:
            print(f"GHCR request failed ({r.status_code}) for {image}")
            return []

        data = r.json()
        return data.get("tags", []) or []

    except Exception as e:
        print(f"Could not reach GHCR for {image}: {e}")
        return []

def get_current_ssmt_image_version(use_production: bool = False) -> str:
    """
    Returns the **latest** tag whose base version exactly matches BASE_VERSION.
    Example: if BASE_VERSION = "2.0.0", returns highest "2.0.0.x" found.
    Falls back to BASE_VERSION.0 if no matching tags exist.
    """
    image = GHCR_PRODUCTION if use_production else GHCR_STAGING
    token = _get_github_token()

    all_tags = _fetch_all_tags(image, token)
    if not all_tags:
        print(f"No tags found for {image} → using {BASE_VERSION}.0")
        return f"{BASE_VERSION}.0"

    # Filter valid 4-part version tags that match current base
    matching_tags = [
        t for t in all_tags
        if _is_valid_version_tag(t) and _get_base_part(t) == BASE_VERSION
    ]

    if not matching_tags:
        print(f"No tags matching base {BASE_VERSION} found → using {BASE_VERSION}.0")
        return f"{BASE_VERSION}.0"

    # Natural sort → highest first
    sorted_matching = natsorted(matching_tags, reverse=True)
    latest = sorted_matching[0]

    print(f"Latest matching tag ({BASE_VERSION}*) on {image}: {latest}")
    return latest


def get_next_ssmt_image_version(use_production: bool = False) -> str:
    """
    Returns the next recommended version, incrementing the build number
    of the latest matching BASE_VERSION tag.
    """
    current = get_current_ssmt_image_version(use_production)

    parts = current.split(".")
    base = ".".join(parts[:3])
    build = int(parts[3]) if len(parts) == 4 else 0

    # Safety check (should always be true with current logic)
    if base != BASE_VERSION:
        print(f"Warning: current base {base} != expected {BASE_VERSION} → resetting")
        next_version = f"{BASE_VERSION}.0"
    else:
        next_version = f"{BASE_VERSION}.{build + 1}"

    print(f"Next version: {current} → {next_version}")
    return next_version


if __name__ == "__main__":
    import sys

    prod = any(x in sys.argv for x in ["--production", "-p", "--prod"])

    print("=== Current version ===")
    curr = get_current_ssmt_image_version(use_production=prod)
    print(curr)
    print()

    print("=== Next recommended version ===")
    nxt = get_next_ssmt_image_version(use_production=prod)
    print(nxt)