#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

setup_requirements = ['pytest-runner']
test_requirements = ['pytest']

setup(
    author="Clinton Collins"
           "Sharon Chen"
           "Zhaowei Du"
           "Mary Fisher"
           "Clark Kirkman IV"
           "Benoit Raybaud",
    author_email='ccollins@idmod.org, '
                 'schen@idmod.org, '
                 'zdu@idmod.org, '
                 'mfisher@idmod.org'
                 'ckirkman@idmod.org, '
                 'braybaud@idmod.org',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Core tools for modeling",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_local',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='1.0.0',
    zip_safe=False,
)