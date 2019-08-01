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
# python setup_dev_env.py

base_directory = abspath(join(dirname(__name__), '..'))


default_install = ['test']
data_class_default = default_install

# check for 3.6 and add the dataclass backport if needed
if platform.python_version()[:3] == '3.6':
    data_class_default.append('3.6')

idmrepo = '--index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'

# Our packages and the extras to install
packages = dict(
    idmtools_core=data_class_default,
    idmtools_cli=default_install,
    idmtools_platform_local=default_install,
    idmtools_platform_comps=default_install,
    idmtools_models_collection=default_install,
    idmtools_test=[]
)

# loop through and install our packages
for package, extras in packages.items():
    extras_str = f"[{','.join(extras)}]" if extras else ''
    print(f'Installing {package} with extras: {extras_str if extras_str else "None"}')
    result = subprocess.run(["pip", "install", "-e", f".{extras_str}", idmrepo], cwd=join(base_directory, package))
