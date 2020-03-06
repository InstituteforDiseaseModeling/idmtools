#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_core platform, the core tools for modeling and analysis."""
import sys

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

build_requirements = ['flake8', 'coverage', 'py-make', 'bump2version', 'twine']
test_requirements = ['pytest', 'pytest-runner', 'numpy==1.16.4', 'xmlrunner', 'pytest-xdist',
                     'pytest-timeout', 'pytest-cache'] + build_requirements

# check for python 3.6
if sys.version_info[1] == 6:
    requirements.append('dataclasses')

extras = {
    'test': test_requirements,
    # to support notebooks we need docker
    'notebooks': ['docker==4.0.1'],
    'packaging': build_requirements,
    'idm': ['idmtools_platform_comps', 'idmtools_cli', 'idmtools_models'],
    # our full install include all common plugins
    'full': ['idmtools_platform_comps', 'idmtools_platform_local', 'idmtools_cli', 'idmtools_models']
}

authors = [
    ("Ross Carter", "rcarter@idmod.org"),
    ("Sharon Chen", "shchen@idmod.org"),
    ("Clinton Collins", "ccollins@idmod.org"),
    ("Zhaowei Du", "zdu@idmod.org"),
    ("Mary Fisher", "mafisher@idmod.org"),
    ("Mandy Izzo", "mizzo@idmod.org"),
    ("Clark Kirkman IV", "ckirkman@idmod.org"),
    ("Benoit Raybaud", "braybaud@idmod.org"),
    ("Jen Schripsema", "jschripsema@idmod.org")
]

setup(
    author=[author[0] for author in authors],
    author_email=[author[1] for author in authors],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework:: IDM-Tools'
    ],
    description="Core tools for modeling",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools',
    packages=find_packages(exclude=["tests"]),
    entry_points=dict(
        idmtools_experiment=["idmtools_experiment = idmtools.entities.experiment:ExperimentSpecification"],
        idmtools_task=  # noqa: E251
                      ["idmtools_task_command = idmtools.entities.command_task:CommandTaskSpecification"]
        ),
    test_suite='tests',
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.3.0+nightly',
    zip_safe=False
)
