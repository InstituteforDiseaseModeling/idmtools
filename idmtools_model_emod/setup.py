#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_model_emod platform to support EMOD model users."""
import itertools

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

build_requirements = ['flake8', 'coverage', 'py-make', 'bump2version', 'twine']
setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'pytest-timeout', 'pytest-cache'] + build_requirements
# special features targeted for internal idm users and developers. We will force users to install through extras
# since it adds a bit of unnecessary overhead
bamboo_requriements = [
    'atlassian-python-api~=1.14.2',
    'keyring',
    'requests'
]

extras = dict(test=test_requirements, packaging=build_requirements, bamboo=bamboo_requriements)
extras['all'] = list(itertools.chain(extras.values()))

authors = [
    ("Ross Carter", 'rcarter@idmod.org'),
    ("Sharon Chen", 'shchen@idmod.org'),
    ("Ye Chen", 'yechen@idmod.org'),
    ("Clinton Collins", 'ccollins@idmod.org'),
    ("Zhaowei Du", "zdu@idmod.org"),
    ("Mary Fisher", 'mafisher@idmod.org'),
    ("Mandy Izzo", 'mizzo@idmod.org'),
    ("Clark Kirkman IV", 'ckirkman@idmod.org'),
    ("Benoit Raybaud", "braybaud@idmod.org"),
    ("Jen Schripsema", "jschripsema@idmod.org")
]

setup(
    author=[author[0] for author in authors],
    author_email=[author[1] for author in authors],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework:: IDM-Tools :: models'
    ],
    description="Core tools for modeling",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_model_emod',
    entry_points=dict(),
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.3.0+nightly',
    zip_safe=False,
)
