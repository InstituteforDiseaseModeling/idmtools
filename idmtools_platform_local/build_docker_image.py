####
# This script is currently a workaround so that we can use bump2version with docker since the nightly versions
# don't work with docker registry
import glob
import os
import shutil
import subprocess
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOCAL_PACKAGE_DIR = os.path.join(BASE_DIR, 'idmtools_platform_local')

version = open('VERSION').read().strip()
if '+nightly' in version:
    version = version.replace('+nightly', '.nightly')

os.makedirs(os.path.abspath('.depends'), exist_ok=True)
for root, dirs, files in os.walk(os.path.join(LOCAL_PACKAGE_DIR, '.depends')):
    for file in files:
        os.remove(os.path.join(root, file))
for package in ['idmtools_core']:
    for file in glob.glob(os.path.join(BASE_DIR, package, 'dist', '**.gz')):
        shutil.copy(file, os.path.join(LOCAL_PACKAGE_DIR, '.depends', os.path.basename(file)))

cmd = ['docker', 'build', '--network=host', '--tag',
       f'idm-docker-staging.packages.idmod.org/idmtools/local_workers:{version}', '.']
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
sys.exit(p.returncode)
