#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

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
              ui=['flask~=1.0.3','Flask-AutoIndex~=0.6.4', 'flask_restful~=0.3.7'])

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
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.1.0',
    zip_safe=False,
)