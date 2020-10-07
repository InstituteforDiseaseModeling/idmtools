#!/usr/bin/env python
import shutil

import logging
import os
import subprocess
import sys
import unicodedata
from logging import getLogger
from os.path import abspath, join, dirname
from typing import List, Generator

# on windows virtual env is not populated through pymake
if sys.platform == "win32" and 'VIRTUAL_ENV' in os.environ:
    sys.path.insert(0, os.environ['VIRTUAL_ENV'] + "\\Lib\\site-packages")

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

logger = getLogger("bootstrap")
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
file_handler = logging.FileHandler("bootstrap.buildlog")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
# use colorful logs except the first time
console_log_level = logging.DEBUG if 'BUILD_DEBUG' in os.environ else logging.INFO
try:
    import coloredlogs

    coloredlogs.install(logger=logger, level=console_log_level, fmt="%(asctime)s [%(levelname)-8.8s]  %(message)s")
    logging.addLevelName(15, 'VERBOSE')
    logging.addLevelName(35, 'SUCCESS')
    logging.addLevelName(50, 'CRITICAL')
except ImportError:
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_log_level)
    logger.addHandler(console_handler)

script_dir = abspath(join(dirname(__file__)))
base_directory = abspath(join(script_dir, '..'))

default_install = ['test']
data_class_default = default_install

idmrepo = '--extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple'

# Our packages and the extras to install
packages = dict(
    idmtools_core=data_class_default,
    idmtools_cli=default_install,
    idmtools_platform_local=data_class_default + ['workers', 'ui'],
    idmtools_platform_comps=data_class_default,
    idmtools_models=data_class_default,
    idmtools_platform_slurm=data_class_default,
    idmtools_test=[]
)


def execute(cmd: List['str'], cwd: str) -> Generator[str, None, None]:
    """
    Runs a command and filters output

    Args:
        cmd: Command to run
        cwd: Working directory

    Returns:
        Generator returning each line

    Raises:
        CalledProcessError if the return code was not 0
    """
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, cwd=cwd)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


escapes = ''.join([chr(char) for char in range(1, 32)])
translator = str.maketrans('', '', escapes)


def process_output(output_line: str):
    """
    Process output

    Args:
        output_line: Output line

    Returns:
        None. Instead prints to log level on screen
    """
    # catch errors where possible
    if "FAILED [" in output_line:
        logger.critical(output_line.strip())
    elif any([s in output_line for s in ["Successfully", "SUCCESS"]]):
        logger.log(35, output_line.strip())
    elif any([s in output_line for s in ["WARNING", "SKIPPED"]]):
        logger.warning(output_line.strip())
    else:
        output_line = output_line.strip().translate(translator)
        logger.debug("".join(ch for ch in output_line if unicodedata.category(ch)[0] != "C"))


# install wheel first to benefit from binaries
for line in execute(["pip", "install", "wheel"], cwd=join(base_directory, 'docs')):
    process_output(line)

# loop through and install our packages
for package, extras in packages.items():
    extras_str = f"[{','.join(extras)}]" if extras else ''
    logger.info(f'Installing {package} with extras: {extras_str if extras_str else "None"} from {base_directory}')
    try:
        for line in execute(["pip", "install", "-e", f".{extras_str}", idmrepo], cwd=join(base_directory, package)):
            process_output(line)
        result = 0
    except subprocess.CalledProcessError as e:
        logger.critical(f'{package} installed failed using {e.cmd} did not succeed')
        result = e.returncode
        logger.debug(f'Return Code: {result}')

for line in execute(["pip", "install", "-r", "requirements.txt"], cwd=join(base_directory, 'docs')):
    process_output(line)

# dev idmtools ini
dev_idmtools_ini = join(base_directory, "examples", "idmtools.ini")
if os.path.exists:
    logger.critical("Placing development ini in examples. This will redirect all request to production to staging!")
shutil.copy(join(script_dir, "examples_idmtools.ini"), join(base_directory, "examples", "idmtools.ini"))