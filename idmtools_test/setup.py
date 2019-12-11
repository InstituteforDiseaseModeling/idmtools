#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

setup_requirements = []

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
        'Framework:: IDM-Tools :: Test',
    ],
    description="Test and demo data for IDM-Tools",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM, test, testdata, demodata',
    name='idmtools_test',
    packages=find_packages(),
    setup_requires=setup_requirements,
    entry_points=dict(idmtools_platform=  # noqa: E251
                      ["idmtools_platform_test = idmtools_test.utils.test_platform:TestPlatformSpecification"],
                      idmtools_model=  # noqa: E251
                      ["idmtools_model_test = idmtools_test.utils.tst_experiment_spec:TstExperimentSpec"]
                      ),
    test_suite='tests',
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.3.0+nightly',
    zip_safe=False
)
