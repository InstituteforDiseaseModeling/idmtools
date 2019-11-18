#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

build_requirements = ['flake8', 'coverage', 'py-make', 'bump2version']
setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'numpy==1.16.4', 'xmlrunner', 'pytest-timeout', 'pytest-cache'] + build_requirements

extras = {
    'test': test_requirements,
    'dev': build_requirements,
    'packaging': build_requirements
}

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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework:: IDM-Tools :: CLI'
    ],
    description="CLI for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM, cli',
    name='idmtools_cli',
    packages=find_packages(exclude=["tests"]),
    setup_requires=setup_requirements,
    test_suite='tests',
    entry_points={"console_scripts": ["idmtools=idmtools_cli.main:main"]},
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.2.0+nightly',
    zip_safe=False
)
