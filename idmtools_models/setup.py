#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_models platform, core tools for other models such as Python and R models."""
import sys

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

build_requirements = ['flake8', 'coverage', 'bump2version', 'twine']
setup_requirements = []
test_requirements = ['pytest', 'pytest-runner', 'pytest-timeout', 'pytest-cache'] + build_requirements

extras = dict(test=test_requirements, packaging=build_requirements)

# check for python 3.7
if sys.version_info[0] == 3 and sys.version_info[1] == 7 and sys.version_info[2] < 3:
    raise EnvironmentError("Python 3.7 requires 3.7.3 or higher")

authors = [
    ("Ross Carter", "rcarter@idmod.org"),
    ("Sharon Chen", "shchen@idmod.org"),
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Framework:: IDM-Tools :: models'
    ],
    description="Core tools for modeling",
    install_requires=requirements,
    long_description=readme,
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools_models',
    entry_points=dict(idmtools_task=  # noqa E521
                      ["idmtools_task_python = idmtools_models.python.python_task:PythonTaskSpecification",
                       "idmtools_task_python_json = idmtools_models.python.json_python_task:JSONConfiguredPythonTaskSpecification",
                       "idmtools_task_templated_script = idmtools_models.templated_script_task:TemplatedScriptTaskSpecification",
                       "idmtools_task_wrapper_script = idmtools_models.templated_script_task:ScriptWrapperTaskSpecification",
                       "idmtools_task_r = idmtools_models.r.r_task:RTaskSpecification",
                       "idmtools_task_r_json = idmtools_models.r.json_r_task:JSONConfiguredRTaskSpecification",
                       "idmtools_task_json = idmtools_models.json_configured_task:JSONConfiguredTaskSpecification"
                       ]
                      ),
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite='tests',
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version='1.7.10+nightly'
)
