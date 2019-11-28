#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

build_requirements = ['flake8', 'coverage', 'py-make', 'bump2version', 'twine']
setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'pytest-timeout', 'pytest-cache'] + build_requirements

extras = dict(test=test_requirements, packaging=build_requirements)

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
        'Framework:: IDM-Tools :: models'
    ],
    description="Core tools for modeling",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_models',
    entry_points=dict(idmtools_model=  # noqa: E251
                      ["idmtools_model_python = idmtools_models.python.python_experiment_spec:PythonExperimentSpec",
                       "idmtools_model_r = idmtools_models.r.r_experiment_spec:RExperimentSpec"],
                      idmtools_task=
                      ["idmtools_task_python = idmtools_models.python.python_task:PythonTaskSpecification",
                       "idmtools_task_python_json = idmtools_models.python.python_task:JSONConfiguredPythonTaskSpecification",
                       "idmtools_task_r = idmtools_models.r.r_task:RTaskSpecification",
                       "idmtools_task_r_json = idmtools_models.r.r_task:JSONConfiguredRTaskSpecification",
                       "idmtools_task_json = idmtools_models.json_configured_task:JSONConfiguredTaskSpecification",
                       "idmtools_docker = idmtools_models.docker_task:DockerTaskSpecification"
                       ]
                      ),
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='0.2.0+nightly',
    zip_safe=False,
)
