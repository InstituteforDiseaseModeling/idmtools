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

extras = dict(test=test_requirements, dev=['Pympler'])

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
        'Framework:: idmtools :: Platform',
    ],
    description="Comps platform for idmtools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_platform_comps',
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    entry_points=dict(idmtools_platform=
                      ["idmtools_platform_comps = idmtools_platform_comps.plugin_info:COMPSSpecification"],
                      idmtools_platform_cli=
                      ["idmtools_platform_cli_comps = idmtools_platform_comps.comps_cli:LocalCLISpecification"]
                      ),
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.1.0',
    zip_safe=False,
)
