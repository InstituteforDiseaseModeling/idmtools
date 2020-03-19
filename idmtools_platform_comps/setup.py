#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_platform_comps platform, for users who use the COMPS platform for IDM-Tools."""
import sys

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

setup_requirements = []
build_requirements = ['flake8', 'coverage', 'py-make', 'bump2version', 'twine']
test_requirements = ['pytest', 'pytest-runner', 'matplotlib', 'pytest-timeout', 'pytest-cache'] + build_requirements

extras = dict(test=test_requirements, dev=['Pympler'], packaging=build_requirements)

# check for python 3.6
if sys.version_info[1] == 6:
    requirements.append('dataclasses')

authors = [
    ("Ross Carter", "rcarter@idmod.org"),
    ("Sharon Chen", "shchen@idmod.org"),
    ("Ye Chen", "yechen@idmod.org"),
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
        'Framework:: IDM-Tools :: Platform',
    ],
    description="Comps platform for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_platform_comps',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    entry_points=dict(idmtools_platform=  # noqa: E251
                      ["idmtools_platform_comps = idmtools_platform_comps.plugin_info:COMPSPlatformSpecification",
                       "idmtools_platform_ssmt = idmtools_platform_comps.plugin_info:SSMTPlatformSpecification"]
                      ),
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='1.0.0+nightly',
    zip_safe=False,
)
