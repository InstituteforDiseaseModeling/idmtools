#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_slurm_utils."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

# Load our Requirements files
with open('requirements.txt') as requirements_file:
    requirements = [dependency for dependency in requirements_file.read().split("\n") if not dependency.startswith("--")]

build_requirements = ['flake8', 'coverage', 'bump2version']
setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'xmlrunner', 'pytest-timeout', 'pytest-cache'] + build_requirements

extras = {
    'test': test_requirements,
    'dev': build_requirements,
    'packaging': build_requirements
}

authors = [
    ("Clinton Collins", "ccollins@idmod.org"),
]

setup(
    author=", ".join([author[0] for author in authors]),
    author_email=", ".join([author[1] for author in authors]),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    description="idmtools slurm utils",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools-slurm-utils',
    packages=find_packages(),
    setup_requires=[],
    python_requires='>=3.6.*, !=3.7.0, !=3.7.1, !=3.7.2',
    test_suite='tests',
    extras_require=extras,
    entry_points={
        'console_scripts': [
            'idmtools-slurm-bridge = idmtools_slurm_utils.singularity_bridge:main',
        ],
    },
    version='1.6.7+nightly'
)