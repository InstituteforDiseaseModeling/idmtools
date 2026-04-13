"""Utility script to get installed package version number."""
from importlib.metadata import version, PackageNotFoundError

packages = [
    "idmtools",
    "idmtools_cli",
    "idmtools_platform_comps",
    "idmtools_models",
    "idmtools_platform_general",
    "idmtools_platform_slurm",
    "idmtools_platform_container",
    "idmtools_test"
]

for pkg in packages:
    try:
        print(f"{pkg}: {version(pkg)}")
    except PackageNotFoundError:
        print(f"{pkg}: not installed")
