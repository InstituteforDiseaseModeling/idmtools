#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_slurm_utils."""
import os
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

# Load our Requirements files
extra_require_files = dict()
for file_prefix in ['', 'dev_', 'build_']:
    filename = f'{file_prefix}requirements'
    if os.path.exists(f'{filename}.txt'):
        with open(f'{filename}.txt') as requirements_file:
            extra_require_files[file_prefix.strip("_") if file_prefix else filename] = [dependency for dependency in requirements_file.read().split("\n") if not dependency.startswith("--")]

build_requirements = ['flake8', 'coverage', 'bump2version']
if 'dev' in extra_require_files:
    build_requirements += extra_require_files['dev']
    build_requirements = list(set(build_requirements))

setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'pytest-timeout', 'pytest-cache'] + build_requirements

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
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    description="idmtools slurm utils",
    install_requires=extra_require_files['requirements'],
    long_description=None,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools-slurm-utils',
    packages=find_packages(exclude=["tests"]),
    setup_requires=[],
    test_suite='tests',
    extras_require=extras,
    entry_points={
        'console_scripts': [
            'idmtools-slurm-bridge = idmtools_slurm_utils.singularity_bridge:main',
        ],
    },
    version='1.7.10+nightly'
)
