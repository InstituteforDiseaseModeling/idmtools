#!/usr/bin/env python
"""Utility script to update references to idmtools_core in requirements.txt files when versions change."""
import os
import glob
import re
import tomllib  # use 'tomli' if you're on Python <3.11
import tomli_w  # write support; install with `pip install tomli-w`

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CORE_PATH = os.path.join(REPO_PATH, 'idmtools_core')


def get_current_version() -> str:
    """Find current version of idmtools_core.

    Returns:
        Current version of idmtools_core.
    """
    with open(os.path.join(CORE_PATH, "pyproject.toml"), "rb") as f:
        data = tomllib.load(f)

    version = data["project"]["version"]
    return version


version = get_current_version()
print(version)