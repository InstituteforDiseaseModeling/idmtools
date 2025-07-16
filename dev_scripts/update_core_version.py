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


def update_idmtools_version_in_pyproject():  # noqa: D103
    target_pattern = re.compile(r'^idmtools([ \t]*(==|~=|>=|<=)?[ \t]*[\d\.]+)?$')

    current_version = get_current_version()
    new_dependency = f"idmtools~={current_version}"

    for file in glob.glob(os.path.join(REPO_PATH, "**", "pyproject.toml"), recursive=True):
        with open(file, "rb") as f:
            try:
                pyproject_data = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                print(f"Skipping {file} due to TOML parse error: {e}")
                continue

        dependencies = pyproject_data.get("project", {}).get("dependencies", [])
        updated = False

        for i, dep in enumerate(dependencies):
            if target_pattern.match(dep):
                if dep != new_dependency:
                    print(f"Updating {file}: {dep} → {new_dependency}")
                    dependencies[i] = new_dependency
                    updated = True

        if updated:
            # Write updated TOML back using tomli_w
            with open(file, "wb") as f:
                tomli_w.dump(pyproject_data, f)


update_idmtools_version_in_pyproject()
# TODO, need to update pyproject.toml in all idmtools_platform_general, idmtools_platform_container, idmtools_platform_slurm for other dependencies as well.
