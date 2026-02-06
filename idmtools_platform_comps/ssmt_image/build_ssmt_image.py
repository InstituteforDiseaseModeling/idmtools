"""This script builds and optionally pushes Docker images to GitHub Container Registry (ghcr.io).

Notes:
    Authentication options:
    1. GitHub Personal Access Token (PAT) with packages:write scope
       Set GITHUB_TOKEN environment variable
    2. Docker login: docker login ghcr.io -u USERNAME -p TOKEN
    3. GitHub Actions: Automatically authenticated when using GITHUB_TOKEN

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import argparse
import glob
import os
import shutil
import subprocess
from logging import getLogger, basicConfig, DEBUG, INFO
import sys
from getpass import getpass
import keyring
from idmtools_platform_comps.utils.package_version_new import get_next_docker_image_version_from_ghcr, GHCR_PRODUCTION, GHCR_STAGING

logger = getLogger(__name__)

# Global Configurations
KEYRING_NAME = "idmtools_ssmt_builder_ghcr"


CURRENT_DIRECTORY = os.path.dirname(__file__)
logger.info("Building Docker image for GitHub Container Registry (ghcr.io)")
BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIRECTORY, '..', '..'))
LOCAL_PACKAGE_DIR = os.path.join(BASE_DIR, 'idmtools_platform_comps/ssmt_image')


def get_dependency_packages():
    """
    Get python packages required to build image.

    Returns:
        None
    """
    os.makedirs(os.path.abspath('.depends'), exist_ok=True)
    for root, _dirs, files in os.walk(os.path.join(LOCAL_PACKAGE_DIR, '.depends')):
        for file in files:
            os.remove(os.path.join(root, file))
    for package in ['idmtools_core', 'idmtools_models', 'idmtools_platform_comps']:
        for file in glob.glob(os.path.join(BASE_DIR, package, 'dist', '**.gz')):
            shutil.copy(file, os.path.join(LOCAL_PACKAGE_DIR, '.depends', os.path.basename(file)))


def get_github_token(disable_keyring_load=False, disable_keyring_save=False):
    """
    Get GitHub token for authentication with ghcr.io.

    Priority order:
    1. GITHUB_TOKEN environment variable (GitHub Actions)
    2. GH_TOKEN environment variable (GitHub CLI)
    3. Keyring (if not disabled)
    4. User prompt

    Args:
        disable_keyring_load: Disable loading token from keyring
        disable_keyring_save: Disable saving token to keyring

    Returns:
        tuple: (username, token)
    """
    # Try environment variables first
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')

    if token:
        logger.info("Using GitHub token from environment variable")
        # For ghcr.io, username can be anything when using PAT
        username = os.environ.get('GITHUB_ACTOR', 'token')
        return username, token

    # Try keyring
    if not disable_keyring_load:
        stored_token = keyring.get_password(KEYRING_NAME, "github_token")
        if stored_token:
            logger.info("Using GitHub token from keyring")
            username = keyring.get_password(KEYRING_NAME, "github_username") or 'token'
            return username, stored_token

    # Prompt user
    print("\nGitHub Container Registry Authentication Required")
    print("=" * 50)
    print("You need a GitHub Personal Access Token (PAT) with 'packages:write' scope")
    print("Create one at: https://github.com/settings/tokens/new")
    print("Required scopes: write:packages, read:packages")
    print("=" * 50)

    username = input('GitHub Username (or leave blank to use "token"): ').strip() or 'token'
    token = getpass(prompt='GitHub Personal Access Token: ')

    if not disable_keyring_save:
        logger.info("Saving credentials to keyring")
        keyring.set_password(KEYRING_NAME, "github_token", token)
        keyring.set_password(KEYRING_NAME, "github_username", username)

    return username, token


def docker_login_ghcr(username, token):
    """
    Login to GitHub Container Registry using docker login.

    Args:
        username: GitHub username
        token: GitHub Personal Access Token

    Returns:
        bool: True if login successful, False otherwise
    """
    logger.info("Logging into ghcr.io...")

    cmd = ['docker', 'login', 'ghcr.io', '-u', username, '--password-stdin']

    try:
        result = subprocess.run(
            cmd,
            input=token.encode(),
            capture_output=True,
            text=False,
            check=False
        )

        if result.returncode == 0:
            logger.info("Successfully logged into ghcr.io")
            return True
        else:
            logger.error(f"Docker login failed: {result.stderr.decode()}")
            return False

    except Exception as e:
        logger.error(f"Error during docker login: {e}")
        return False


def build_image(username, token, disable_keyring_load, disable_keyring_save, use_production, push, skip_login):
    """
    Build (and optionally push) the Docker image to GitHub Container Registry.

    Args:
        username: GitHub username
        token: GitHub Personal Access Token
        disable_keyring_load: Disable loading credentials from keyring
        disable_keyring_save: Disable saving credentials to keyring
        use_production: Use production image name instead of staging
        push: Push image after building
        skip_login: Skip docker login step

    Returns:
        int: Exit code
    """
    # Get GitHub token if not provided
    if username is None or token is None:
        username, token = get_github_token(disable_keyring_load, disable_keyring_save)

    # Select image repository
    image = GHCR_PRODUCTION if use_production else GHCR_STAGING
    logger.info(f"Target image: {image}")

    # Login to ghcr.io if pushing and not skipping login
    if push and not skip_login:
        if not docker_login_ghcr(username, token):
            logger.error("Docker login failed. Cannot push image.")
            return 1

    # Get dependency packages
    logger.info("Collecting dependency packages...")
    get_dependency_packages()

    # Get next version
    logger.info("Determining next version...")

    version = get_next_docker_image_version_from_ghcr()

    # Build Docker image
    build_cmd = [
        'docker', 'build',
        '--network=host',
        '--build-arg', f'SSMT_VERSION={version}',
        '--tag', f'{image}:{version}',
        '--tag', f'{image}:latest',
        '.'
    ]

    logger.info(f'Building image: {" ".join(build_cmd)}')

    build_process = subprocess.Popen(
        " ".join(build_cmd),
        cwd=os.path.abspath(os.path.dirname(__file__)),
        shell=True
    )
    build_process.wait()

    if build_process.returncode != 0:
        logger.error("Docker build failed")
        return build_process.returncode

    logger.info(f"Successfully built image: {image}:{version}")

    # Tag additional versions for convenience
    # Full version: 3.0.0.5
    # Base version: 3.0.0 (without build number)
    # Latest: latest

    version_parts = version.split('.')
    if len(version_parts) >= 4:
        # Tag base version (3.0.0.5 -> 3.0.0)
        base_version = '.'.join(version_parts[:3])
        tag_cmd = f'docker tag {image}:{version} {image}:{base_version}'
        logger.info(f"Creating base version tag: {base_version}")
        os.system(tag_cmd)
    else:
        logger.warning(f"Unexpected version format: {version}")
        base_version = None

    # Push images if requested
    if push:
        logger.info("Pushing images to ghcr.io...")

        # Determine which tags to push
        tags_to_push = [version, 'latest']
        if base_version:
            tags_to_push.append(base_version)

        for tag in tags_to_push:
            push_cmd = f'docker push {image}:{tag}'
            logger.info(f"Pushing: {image}:{tag}")

            push_result = os.system(push_cmd)

            if push_result != 0:
                logger.error(f"Failed to push {image}:{tag}")
                return push_result

            logger.info(f"Successfully pushed: {image}:{tag}")

        logger.info(f"All tags pushed successfully for version {version}")
    else:
        logger.info("Skipping push (use --push to push to registry)")
        logger.info("To push manually, run:")
        logger.info(f"  docker push {image}:{version}")
        if base_version:
            logger.info(f"  docker push {image}:{base_version}")
        logger.info(f"  docker push {image}:latest")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build and push Docker images to GitHub Container Registry (ghcr.io)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build only (staging)
  python build_docker_image.py

  # Build and push to staging
  python build_docker_image.py --push

  # Build and push to production
  python build_docker_image.py --push --production

  # Use environment variable for token
  export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
  python build_docker_image.py --push

Authentication:
  Set GITHUB_TOKEN or GH_TOKEN environment variable, or you will be prompted.
  Token needs 'write:packages' and 'read:packages' scopes.
  Create at: https://github.com/settings/tokens/new
        """
    )

    parser.add_argument("--username", default=None,
                        help="GitHub username (default: uses 'token' or GITHUB_ACTOR)")
    parser.add_argument("--token", default=None, dest="password",
                        help="GitHub Personal Access Token (or set GITHUB_TOKEN env var)")
    parser.add_argument("--disable-keyring-load", action="store_true",
                        help="Disable loading token from keyring")
    parser.add_argument("--disable-keyring-save", action="store_true",
                        help="Disable saving token to keyring")
    parser.add_argument("--production", action="store_true",
                        help="Use production image repository instead of staging")
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
    basicConfig(filename="build.log", level=DEBUG if any([args.verbose, args.debug]) else INFO)

    # Run build
    exit_code = build_image(
        args.username,
        args.password,
        args.disable_keyring_load,
        args.disable_keyring_save,
        args.production,
        args.push,
        args.skip_login
    )

    sys.exit(exit_code)
