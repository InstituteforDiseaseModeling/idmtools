#!/usr/bin/env python
"""Utility script to update references to idmtools_core in requirements.txt files when versions change."""
import glob
import os
import re

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CORE_PATH = os.path.join(REPO_PATH, 'idmtools_core')


def get_current_version() -> str:
    """Find current version of idmtools_core.

    Returns:
        Current version of idmtools_core.
    """
    with open(os.path.join(CORE_PATH, '.bumpversion.cfg')) as vin:
        contents = vin.read()
        for line in contents.split('\n'):
            if 'current_version' in line:
                current_version = line.split('=')[1].strip()
    return current_version


def update_requirements():
    """
    Find all the files with idmtools core as dependency and updates.

    Returns:
        None
    """
    core_expr = re.compile(r'idmtools([~=]+[+0-9.a-z]+)?$', re.MULTILINE)
    current_version = get_current_version()
    for file in glob.glob(os.path.join(REPO_PATH, f'**{os.path.sep}requirements.txt')):
        with open(file, 'r') as rin:
            contents = rin.read()
            new_contents = core_expr.sub(f'idmtools~={current_version}', contents)
            if contents != new_contents:
                print(f'Updated {file}')
        with open(file, 'w') as rout:
            rout.write(new_contents)


update_requirements()
