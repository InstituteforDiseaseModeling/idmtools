#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_platform_comps platform, for users who use the COMPS platform for idmtools."""
from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

build_requirements = ['flake8', 'coverage', 'bump2version', 'twine', "natsort"]
test_requirements = ['pytest', 'pytest-runner', 'matplotlib', 'pytest-timeout', 'pytest-cache', 'pytest-lazy-fixture'] + build_requirements

extras = dict(test=test_requirements, dev=['Pympler'], packaging=build_requirements)

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
    author=", ".join([author[0] for author in authors]),
    author_email=", ".join([author[1] for author in authors]),
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    description="Comps platform for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_platform_comps',
    packages=find_packages(exclude=["tests"]),
    test_suite='tests',
    entry_points="""
[idmtools_platform]
idmtools_platform_comps = idmtools_platform_comps.plugin_info:COMPSPlatformSpecification
idmtools_platform_ssmt = idmtools_platform_comps.plugin_info:SSMTPlatformSpecification
[idmtools_cli.cli_plugins]
comps_subcommand=idmtools_platform_comps.cli.comps:comps
[console_scripts]
comps-cli=idmtools_platform_comps.cli.comps:comps
""",
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='2.1.0+nightly'
)
