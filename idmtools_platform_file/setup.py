#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_platform_file platform, for users who use the COMPS platform for idmtools."""
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
        'Framework:: IDM-Tools :: Platform',
    ],
    description="File platform for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_platform_file',
    packages=find_packages(),
    test_suite='tests',

    entry_points="""
[idmtools_platform]
idmtools_platform_file = idmtools_platform_file.plugin_info:FilePlatformSpecification
""",
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='1.7.4'
)