#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_test module to run extended tests and provide demo date for idmtools tests."""
import sys

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

setup_requirements = []

if sys.platform in ["win32", "cygwin"]:
    requirements.append('pypiwin32==223')
    requirements.append('pywin32')

authors = [
    ("Sharon Chen", "schen@idmod.org"),
    ("Ye Chen", "yechen@idmod.org"),
    ("Clinton Collins", "ccollins@idmod.org"),
    ("Zhaowei Du", "zdu@idmod.org"),
    ("Mary Fisher", "mfisher@idmod.org"),
    ("Clark Kirkman IV", "ckirkman@idmod.org"),
    ("Benoit Raybaud", "braybaud@idmod.org")
]

setup(
    author=[author[0] for author in authors],
    author_email=[author[1] for author in authors],
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ],
    description="Test and demo data for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='modeling, IDM, test, testdata, demodata',
    name='idmtools_test',
    packages=find_packages(exclude=["tests"]),
    setup_requires=setup_requirements,
    entry_points=dict(
        idmtools_platform=["idmtools_platform_test = idmtools_test.utils.test_platform:TestPlatformSpecification", "idmtools_platform_testex = idmtools_test.utils.test_execute_platform:TestExecutePlatformSpecification"],
        idmtools_task=["idmtools_model_test = idmtools_test.utils.test_task:TestTaskSpecification"],
        idmtools_hooks=['idmtools_test_hooks = idmtools_test.test_precreate_hooks']
    ),
    test_suite='tests',
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='2.0.1+nightly',
    zip_safe=False
)
