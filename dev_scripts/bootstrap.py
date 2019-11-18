#!/usr/bin/env python

import platform
import subprocess
from os.path import abspath, join, dirname

# This scripts aids in setup of development environments by installing all the local packages
# defined by packages using development installs.
#
# It is best used
# 1) After the creation of a new virtualenv
# 2) Installing new packages into an existing environment
# 3) Updating existing environments
#
# To use simply run
# python bootstrap.py

base_directory = abspath(join(dirname(__file__), '..'))

default_install = ['test']
data_class_default = default_install

idmrepo = '--extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'

# Our packages and the extras to install
packages = dict(
    idmtools_core=data_class_default,
    idmtools_cli=default_install,
    idmtools_platform_local=data_class_default + ['workers', 'ui'],
    idmtools_platform_comps=data_class_default,
    idmtools_model_emod=data_class_default + ['bamboo'],
    idmtools_models=data_class_default,
    idmtools_test=[]
)

# loop through and install our packages
for package, extras in packages.items():
    extras_str = f"[{','.join(extras)}]" if extras else ''
    print(f'Installing {package} with extras: {extras_str if extras_str else "None"} from {base_directory}')
    result = subprocess.run(["pip", "install", "-e", f".{extras_str}", idmrepo], cwd=join(base_directory, package))
