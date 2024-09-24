"""Define our package group CLI command."""
import os
from logging import getLogger
import click
from typing import Optional, List
from idmtools_cli.cli.entrypoint import cli

user_logger = getLogger('user')


@cli.group(short_help="Contains commands related to package versions.")
def package():
    """Package group cli command."""
    pass


@package.command()
@click.option('--name', required=True, type=str, help="package name")
def latest_version(name: Optional[str]):
    """
    Display the latest version of a package.

    Args:
        name: package name
    """
    from idmtools_platform_comps.utils.package_version import get_latest_version
    v = get_latest_version(name)
    print(v)


@package.command()
@click.option('--name', required=True, type=str, help="package name")
@click.option('--base_version', required=True, default=None, type=str, help="package version")
def compatible_version(name: Optional[str], base_version: Optional[str]):
    """
    Display the latest compatible version of a package.

    Args:
        name: package name
        base_version: package version
    """
    from idmtools_platform_comps.utils.package_version import get_latest_compatible_version
    v = get_latest_compatible_version(name, base_version)
    print(v)


@package.command()
@click.option('--name', required=True, type=str, help="package name")
@click.option('--all/--no-all', type=bool, default=False, help="package version")
def list_versions(name: Optional[str], all: Optional[bool]):
    """
    Display all package versions.

    Args:
        name: package name
        all: True/False - return all or only released versions
    """
    from idmtools_platform_comps.utils.package_version import fetch_package_versions
    versions = fetch_package_versions(name, not all)
    print(versions)


@package.command()
@click.argument('requirement', type=click.Path(exists=True), required=False)
@click.option('--pkg', multiple=True, help="Package for override. Format: 'key==value'")
@click.option('--wheel', multiple=True, help="Local wheel file")
def updated_requirements(requirement: str = None, pkg: Optional[List[str]] = None, wheel: Optional[List[str]] = None):
    """
    Build Updated_Requirements from requirement file.

    Args:
        requirement: Path to requirement file
        pkg: package name (along with version)
        wheel: package wheel file
    """
    from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
        RequirementsToAssetCollection

    pkg_list = list(pkg)
    wheel_list = [os.path.abspath(w) for w in wheel]
    pl = RequirementsToAssetCollection(None, requirements_path=requirement, pkg_list=pkg_list, local_wheels=wheel_list)
    pl.save_updated_requirements()
    req = open('requirements_updated.txt').read()
    print(req)


@package.command()
@click.argument('requirement', type=click.Path(exists=True), required=False)
@click.option('--pkg', multiple=True, help="Package for override. Format: 'key==value'")
@click.option('--wheel', multiple=True, help="Local wheel file")
def checksum(requirement: str = None, pkg: Optional[List[str]] = None, wheel: Optional[List[str]] = None):
    """
    Construct checksum from requirement file.

    Args:
        requirement: path to requirement file
        pkg: package name (along with version)
        wheel: package wheel file
    """
    from idmtools_platform_comps.utils.python_requirements_ac.requirements_to_asset_collection import \
        RequirementsToAssetCollection

    pkg_list = list(pkg)
    wheel_list = [os.path.abspath(w) for w in wheel]
    pl = RequirementsToAssetCollection(None, requirements_path=requirement, pkg_list=pkg_list, local_wheels=wheel_list)
    print(pl.checksum)
