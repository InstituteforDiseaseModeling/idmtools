#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script for the idmtools_core platform, the core tools for modeling and analysis."""
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

extra_require_files = dict()
for file_prefix in ['', 'dev_', 'build_']:
    filename = f'{file_prefix}requirements'
    with open(f'{filename}.txt') as requirements_file:
        extra_require_files[file_prefix.strip("_") if file_prefix else filename] = [dependency for dependency in requirements_file.read().split("\n") if not dependency.startswith("--")]

# Conditional dependency based on Python version
conditional_requirements = ['importlib_metadata; python_version < "3.8"']

version = '2.1.0+nightly'

extras = {
    'test': extra_require_files['build'] + extra_require_files['dev'],
    # to support notebooks we need docker
    'notebooks': ['docker==4.0.1'],
    'packaging': extra_require_files['build'],
    'idm': ['idmtools_platform_comps', 'idmtools_cli', 'idmtools_models'],
    # our full installation includes all common plugins
    'full': ['idmtools_platform_comps', 'idmtools_cli', 'idmtools_models', 'idmtools_platform_general', 'idmtools_platform_slurm', 'idmtools_platform_container'],
    # container install include all container plugins
    'container': ['idmtools_cli', 'idmtools_models', 'idmtools_platform_general', 'idmtools_platform_container'],
    # slurm install include all slurm plugins
    'slurm': ['idmtools_cli', 'idmtools_models', 'idmtools_platform_general', 'idmtools_platform_slurm']

}

authors = [
    ("Ross Carter", "rcarter@idmod.org"),
    ("Sharon Chen", "shchen@idmod.org"),
    ("Clinton Collins", "ccollins@idmod.org"),
    ("Zhaowei Du", "zdu@idmod.org"),
    ("Mary Fisher", "mafisher@idmod.org"),
    ("Mandy Izzo", "mizzo@idmod.org"),
    ("Clark Kirkman IV", "ckirkman@idmod.org"),
    ("Benoit Raybaud", "braybaud@idmod.org"),
    ("Jen Schripsema", "jschripsema@idmod.org"),
    ("Lauren George", "lgeorge@idmod.org"),
    ("Emily Claps", "emily.claps@gatesfoundation.org")
]

setup(
    author=", ".join([author[0] for author in authors]),
    author_email=", ".join([author[1] for author in authors]),
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    description="Core tools for modeling",
    install_requires=extra_require_files['requirements'] + conditional_requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='modeling, IDM',
    name='idmtools',
    packages=find_packages(exclude=["tests"]),
    entry_points=dict(
        idmtools_experiment=["idmtools_experiment = idmtools.entities.experiment:ExperimentSpecification"],
        idmtools_task=["idmtools_task_command = idmtools.entities.command_task:CommandTaskSpecification", "idmtools_task_docker = idmtools.core.docker_task:DockerTaskSpecification"],
        idmtools_hooks=[
            "idmtools_add_git_tag = idmtools.plugins.git_commit",
            "idmtools_id_generate_uuid = idmtools.plugins.uuid_generator",
            "idmtools_id_generate_item_sequence = idmtools.plugins.item_sequence"
        ]
    ),
    python_requires='>=3.8.0',
    test_suite='tests',
    extras_require=extras,
    url='https://github.com/InstituteforDiseaseModeling/idmtools',
    version=version,
    zip_safe=False
)
