import subprocess
from os.path import abspath, join, dirname

# This scripts aids in setup of development environments by installing all the local packages
# defined by packages using development installs.
#
# It is best used
# 1) After the create of a new virtualenv
# 2) Installing new packages into an existing environment
# 3) Updating existing environments

base_directory = abspath(join(dirname(__name__), '..'))

default_install = ['test']
# Our packages and the extras to install
packages = dict(
    idmtools_core=default_install,
    idmtools_cli=default_install,
    idmtools_platform_local=default_install,
    idmtools_platform_comps=default_install,
    idmtools_models_collection=default_install,
    idmtools_test=[]
)

for package, extras in packages.items():
    extras_str = ','.join(extras) if extras else ''
    print(f'Installing {package} with extras: {extras_str if extras_str else "None"}')
    result = subprocess.run(["pip", "install", "-e", f".{extras_str}",
                             '--index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'
                             ],
                            cwd=join(base_directory, package))
