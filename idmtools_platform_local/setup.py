#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
import sys

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

setup_requirements = []
test_requirements = ['pytest', 'pytest-runner']

extras = dict(test=test_requirements, dev=['Pympler'],
              # Requirements for running workers server
              workers=['pandas~=0.24.2', 'sqlalchemy~=1.3.5', 'psycopg2-binary~=2.8.3'],
              # these are only needed when not running UI
              ui=['flask~=1.0.3', 'Flask-AutoIndex~=0.6.4', 'flask_restful~=0.3.7'])

# check for python 3.6
if sys.version_info[1] == 6:
    requirements.append('dataclasses')

authors = [
    ("Sharon Chen", "'schen@idmod.org"),
    ("Clinton Collins", 'ccollins@idmod.org'),
    ("Zhaowei Du", "zdu@idmod.org"),
    ("Mary Fisher", 'mfisher@idmod.org'),
    ("Clark Kirkman IV", 'ckirkman@idmod.org'),
    ("Benoit Raybaud", "braybaud@idmod.org")
]

setup(
    author=[author[0] for author in authors],
    author_email=[author[1] for author in authors],
    classifiers=[
        'Framework:: IDM-Tools :: Platform',
    ],
    description="Provides ability to run models locally using docker containers to IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_platform_local',
    packages=find_packages(),
    setup_requires=setup_requirements,
    entry_points=dict(idmtools_platform=  # noqa: E251
                      ["idmtools_platform_local = idmtools_platform_local.plugin_info:LocalPlatformSpecification"],
                      idmtools_platform_cli=  # noqa: E251
                      ["idmtools_platform_cli_local = idmtools_platform_local.local_cli:LocalCLISpecification"]
                      ),
    test_suite='tests',
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.2.0+nightly',
    zip_safe=False,
)
