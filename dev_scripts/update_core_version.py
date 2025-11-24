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


def update_idmtools_version_in_pyproject():
    """Update idmtools and idmtools_platform_general dependency versions in pyproject.toml files."""
    # Match idmtools or idmtools_platform_general optionally with version specifier
    pattern_idmtools = re.compile(r'^idmtools([ \t]*(==|~=|>=|<=)?[ \t]*[\d\.]+)?$')
    pattern_general = re.compile(r'^idmtools_platform_general([ \t]*(==|~=|>=|<=)?[ \t]*[\d\.]+)?$')
    pattern_cli = re.compile(r'^idmtools_cli([ \t]*(==|~=|>=|<=)?[ \t]*[\d\.]+)?$')

    current_version = get_current_version()
    new_idmtools_dep = f"idmtools~={current_version}"
    new_general_dep = f"idmtools_platform_general~={current_version}"
    new_cli_dep = f"idmtools_cli~={current_version}"

    for file in glob.glob(os.path.join(REPO_PATH, "**", "pyproject.toml"), recursive=True):
        with open(file, "rb") as f:
            try:
                pyproject_data = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                print(f"Skipping {file} due to TOML parse error: {e}")
                continue

        deps = pyproject_data.get("project", {}).get("dependencies", [])
        updated = False

        for i, dep in enumerate(deps):
            if pattern_idmtools.match(dep):
                if dep != new_idmtools_dep:
                    print(f"Updating {file}: {dep} → {new_idmtools_dep}")
                    deps[i] = new_idmtools_dep
                    updated = True

            elif pattern_general.match(dep):
                if dep != new_general_dep:
                    print(f"Updating {file}: {dep} → {new_general_dep}")
                    deps[i] = new_general_dep
                    updated = True

            elif pattern_cli.match(dep):
                if dep != new_cli_dep:
                    print(f"Updating {file}: {dep} → {new_cli_dep}")
                    deps[i] = new_cli_dep
                    updated = True

        # Only write once if something changed
        if updated:
            with open(file, "wb") as f:
                tomli_w.dump(pyproject_data, f)


update_idmtools_version_in_pyproject()
