"""This script builds and optionally pushes Docker images to GitHub Container Registry (ghcr.io).

Copyright 2026, Bill Gates Foundation. All rights reserved.
"""
import argparse
import logging
import os
import subprocess
import sys
import requests
import keyring
import json
from logging import getLogger, basicConfig, DEBUG, INFO
from getpass import getpass
from natsort import natsorted
from typing import Optional, Tuple

logger = getLogger(__name__)

# Global Configurations
KEYRING_NAME = "idmtools_container_ghcr"
GHCR_ORG = "institutefordiseasemodeling"
GHCR_BASE = f'ghcr.io/{GHCR_ORG}'

current_working_directory = os.getcwd()
BASE_VERSION = open(os.path.join(current_working_directory, 'BASE_VERSION')).read().strip()

logger.info("Building Docker image for GitHub Container Registry (ghcr.io)")


def get_github_credentials(disable_keyring_load=False, disable_keyring_save=False) -> Tuple[str, str]:
    """
    Get GitHub credentials for GHCR authentication.

    Priority order:
    1. GITHUB_TOKEN environment variable (GitHub Actions)
    2. GH_TOKEN environment variable (GitHub CLI)
    3. Keyring (if not disabled)
    4. User prompt

    Args:
        disable_keyring_load: Disable loading credentials from keyring
        disable_keyring_save: Disable saving credentials to keyring

    Returns:
        Tuple of (username, token)
    """
    # Try environment variables first
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')

    if token:
        logger.info("Using GitHub token from environment variable")
        username = os.environ.get('GITHUB_ACTOR') or os.environ.get('GITHUB_USERNAME') or 'token'
        return username, token

    # Try keyring
    if not disable_keyring_load:
        try:
            stored_token = keyring.get_password(KEYRING_NAME, "github_token")
            if stored_token:
                logger.info("Using GitHub token from keyring")
                username = keyring.get_password(KEYRING_NAME, "github_username") or 'token'
                return username, stored_token
        except Exception as e:
            logger.debug(f"Could not load from keyring: {e}")

    # Prompt user
    print("\nGitHub Container Registry Authentication Required")
    print("=" * 60)
    print("You need a GitHub Personal Access Token (PAT)")
    print("Create one at: https://github.com/settings/tokens/new")
    print("")
    print("Required scopes:")
    print("  write:packages (to push images)")
    print("  read:packages (to pull images)")
    print("=" * 60)

    username = input('GitHub Username (or press Enter for "token"): ').strip() or 'token'
    token = getpass(prompt='GitHub Personal Access Token: ')

    if not disable_keyring_save and token:
        try:
            logger.info("Saving credentials to keyring")
            keyring.set_password(KEYRING_NAME, "github_token", token)
            keyring.set_password(KEYRING_NAME, "github_username", username)
            print("Credentials saved to keyring")
        except Exception as e:
            logger.warning(f"Could not save to keyring: {e}")

    return username, token


def docker_login_ghcr(username: str, token: str) -> bool:
    """
    Login to GitHub Container Registry.

    Args:
        username: GitHub username
        token: GitHub Personal Access Token

    Returns:
        True if login successful, False otherwise
    """
    logger.info("Logging into ghcr.io...")

    cmd = ['docker', 'login', 'ghcr.io', '-u', username, '--password-stdin']

    try:
        result = subprocess.run(
            cmd,
            input=token.encode(),
            capture_output=True,
            check=False
        )

        if result.returncode == 0:
            logger.info("Successfully logged into ghcr.io")
            print("Logged into ghcr.io")
            return True
        else:
            error_msg = result.stderr.decode() if result.stderr else "Unknown error"
            logger.error(f"Docker login failed: {error_msg}")
            print(f"Login failed: {error_msg}")
            return False

    except Exception as e:
        logger.error(f"Error during docker login: {e}")
        return False


def get_latest_image_version_from_ghcr(image_name: str, token: Optional[str] = None) -> str:
    """
    Fetch the latest image version from GHCR.

    Args:
        image_name: Docker image name (e.g., 'container-rocky-runtime')
        token: Optional GitHub token for authentication

    Returns:
        Latest version string (e.g., '1.0.0.5')
    """
    try:
        # Get authentication token for GHCR API
        auth_url = f"https://ghcr.io/token?scope=repository:{GHCR_ORG}/{image_name}:pull"
        auth_headers = {}

        if token:
            auth_headers['Authorization'] = f'Bearer {token}'

        auth_response = requests.get(auth_url, headers=auth_headers, timeout=10)

        if not auth_response.ok:
            logger.warning(f"Could not authenticate with GHCR for {image_name}")
            logger.info(f"Starting with version {BASE_VERSION}.0")
            return f'{BASE_VERSION}.0'

        bearer_token = auth_response.json().get('token', '')

        # Get tags list
        tags_url = f"https://ghcr.io/v2/{GHCR_ORG}/{image_name}/tags/list"
        headers = {'Authorization': f'Bearer {bearer_token}'}

        response = requests.get(tags_url, headers=headers, timeout=10)

        if response.status_code == 404:
            logger.info(f"Image not found in GHCR. Starting with version {BASE_VERSION}.0")
            return f'{BASE_VERSION}.0'
        elif response.status_code != 200:
            logger.warning(f"Unexpected response code: {response.status_code}")
            return f'{BASE_VERSION}.0'

        tags_data = response.json()
        tags = tags_data.get('tags', [])

        if not tags:
            logger.info(f"No tags found. Starting with version {BASE_VERSION}.0")
            return f'{BASE_VERSION}.0'

        # Filter and sort tags
        version_tags = [t for t in tags if t not in ['latest'] and '.' in t]

        if not version_tags:
            logger.info(f"No version tags found. Starting with version {BASE_VERSION}.0")
            return f'{BASE_VERSION}.0'

        # Sort versions naturally
        sorted_tags = natsorted(version_tags, reverse=True)
        logger.debug(f"Available tags: {sorted_tags[:5]}")

        last_version = sorted_tags[0]
        logger.info(f"Latest version in GHCR: {last_version}")

        # Calculate next version
        version_parts = last_version.split('.')
        base_part = '.'.join(version_parts[:-1])

        if BASE_VERSION in base_part:
            # Increment build number
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            version = '.'.join(version_parts)
        else:
            # Base version changed, start at .0
            version = f'{BASE_VERSION}.0'

        logger.info(f"Next version: {version}")
        return version

    except requests.RequestException as e:
        logger.error(f"Error fetching versions from GHCR: {e}")
        return f'{BASE_VERSION}.0'
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f'{BASE_VERSION}.0'


def build_image(
        username: Optional[str],
        token: Optional[str],
        dockerfile: str,
        image_name: str,
        disable_keyring_load: bool,
        disable_keyring_save: bool,
        push: bool,
        skip_login: bool
) -> int:
    """
    Build (and optionally push) the Docker image to GHCR.

    Args:
        username: GitHub username
        token: GitHub Personal Access Token
        dockerfile: Dockerfile path
        image_name: Docker image name (without registry prefix)
        disable_keyring_load: Disable loading credentials from keyring
        disable_keyring_save: Disable saving credentials to keyring
        push: Push image after building
        skip_login: Skip docker login step

    Returns:
        Exit code (0 for success)
    """
    # Get GitHub credentials if not provided
    if username is None or token is None:
        username, token = get_github_credentials(disable_keyring_load, disable_keyring_save)

    # Full image path
    full_image = f'{GHCR_BASE}/{image_name}'

    print("\n{'=' * 60}")
    print("Building Docker Image for GHCR")
    print("{'=' * 60}")
    print(f"  Image: {full_image}")
    print(f"  Dockerfile: {dockerfile}")
    print("{'=' * 60}\n")

    # Login to GHCR if pushing and not skipping login
    if push and not skip_login:
        if not docker_login_ghcr(username, token):
            logger.error("Docker login failed. Cannot push image.")
            return 1

    # Get next version
    logger.info("Determining next version...")
    version = get_latest_image_version_from_ghcr(image_name, token)

    print(f"Version: {version}\n")

    # Build Docker image
    build_cmd = [
        'docker', 'buildx', 'build',
        '--provenance=false',
        '--output', 'type=docker',  # Load into Docker daemon
        '--network=host',
        '--build-arg', f'CONTAINER_VERSION={version}',
        '--tag', f'{full_image}:{version}',
        '--tag', f'{full_image}:latest',
        '-f', dockerfile,
        '.'
    ]

    logger.info(f'Building: {" ".join(build_cmd)}')
    print(" Building image...\n")

    build_result = subprocess.run(
        build_cmd,
        cwd=current_working_directory
    )

    if build_result.returncode != 0:
        logger.error("Docker build failed")
        print("Build failed")
        return build_result.returncode

    logger.info(f" Successfully built: {full_image}:{version}")
    print("\n Build successful!")

    # Tag base version (e.g., 1.0.0.5 -> 1.0.0)
    version_parts = version.split('.')
    base_version = None

    if len(version_parts) >= 4:
        base_version = '.'.join(version_parts[:-1])

        tag_cmd = ['docker', 'tag', f'{full_image}:{version}', f'{full_image}:{base_version}']
        logger.info(f"Creating base version tag: {base_version}")

        subprocess.run(tag_cmd, check=True)

    # Display tagged images
    print("\n{'=' * 60}")
    print(" Tagged Images")
    print("{'=' * 60}")
    print(f"  {full_image}:{version}")
    if base_version:
        print(f"  {full_image}:{base_version}")
    print(f"  {full_image}:latest")
    print("{'=' * 60}\n")

    # Push if requested
    if push:
        logger.info("Pushing images to ghcr.io...")
        print(" Pushing to GitHub Container Registry...\n")

        # Determine which tags to push
        tags_to_push = [version, 'latest']
        if base_version:
            tags_to_push.append(base_version)

        for idx, tag in enumerate(tags_to_push, 1):
            logger.info(f"Pushing ({idx}/{len(tags_to_push)}): {full_image}:{tag}")
            print(f"  [{idx}/{len(tags_to_push)}] Pushing {tag}...")

            push_cmd = ['docker', 'push', f'{full_image}:{tag}']
            push_result = subprocess.run(push_cmd, capture_output=True, text=True)

            if push_result.returncode != 0:
                logger.error(f" Failed to push {full_image}:{tag}")
                logger.error(f"Error: {push_result.stderr}")
                print(f"      Push failed: {push_result.stderr}")
                return push_result.returncode

            logger.info(" Successfully pushed: {full_image}:{tag}")
            print("       Pushed successfully")

        # Display final summary
        print("\n{'=' * 60}")
        print(" All Images Pushed Successfully")
        print("{'=' * 60}")

        # Get and display image info
        inspect_cmd = ['docker', 'inspect', f'{full_image}:{version}']
        inspect_result = subprocess.run(inspect_cmd, capture_output=True, text=True)

        if inspect_result.returncode == 0:
            try:
                image_info = json.loads(inspect_result.stdout)
                info = image_info[0] if isinstance(image_info, list) else image_info

                size_bytes = info.get('Size', 0)
                size_mb = size_bytes / (1024 ** 2)

                print(f"  Image:   {full_image}")
                print(f"  Version: {version}")
                print(f"  Size:    {size_mb:.2f} MB")
                print(f"  Tags:    {', '.join(tags_to_push)}")
                print("\n  Pull command:")
                print(f"    docker pull {full_image}:{version}")

            except Exception as e:
                logger.debug(f"Could not display image details: {e}")

        print("{'=' * 60}\n")

    else:
        print("\n{'=' * 60}")
        print("  Build Complete - Not Pushed")
        print("{'=' * 60}")
        print("  To push manually, run:")
        print(f"    docker push {full_image}:{version}")
        if base_version:
            print(f"    docker push {full_image}:{base_version}")
        print(f"    docker push {full_image}:latest")
        print("{'=' * 60}\n")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build and push Docker images to GitHub Container Registry (ghcr.io)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build only
  python build_container_image.py

  # Build and push
  python build_container_image.py --push

  # Build with custom Dockerfile and image name
  python build_container_image.py --dockerfile Dockerfile.alpine --image-name container-alpine-runtime --push

  # Use environment variable for token
  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
  python build_container_image.py --push

  # Skip login (if already logged in)
  docker login ghcr.io -u username -p token
  python build_container_image.py --push --skip-login

Authentication:
  Set GITHUB_TOKEN or GH_TOKEN environment variable, or you will be prompted.
  Token needs 'write:packages' and 'read:packages' scopes.
  Create at: https://github.com/settings/tokens/new
        """
    )

    parser.add_argument("--username", default=None,
                        help="GitHub username (default: uses 'token' or GITHUB_ACTOR)")
    parser.add_argument("--token", default=None,
                        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--dockerfile", default="Dockerfile",
                        help="Dockerfile to use for building image (default: Dockerfile)")
    parser.add_argument("--image-name", default="container-rocky-runtime",
                        help="Image name without registry prefix (default: container-rocky-runtime)")
    parser.add_argument("--disable-keyring-load", action="store_true",
                        help="Disable loading token from keyring")
    parser.add_argument("--disable-keyring-save", action="store_true",
                        help="Disable saving token to keyring")
    parser.add_argument("--push", action="store_true",
                        help="Push image to ghcr.io after building")
    parser.add_argument("--skip-login", action="store_true",
                        help="Skip docker login (assumes already logged in)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")

    args = parser.parse_args()

    # Set up logging
    log_level = DEBUG if any([args.verbose, args.debug]) else INFO
    basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("build.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Run build
    try:
        exit_code = build_image(
            args.username,
            args.token,
            args.dockerfile,
            args.image_name,
            args.disable_keyring_load,
            args.disable_keyring_save,
            args.push,
            args.skip_login
        )
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n\n  Build cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print("\n Error: {e}")
        sys.exit(1)
