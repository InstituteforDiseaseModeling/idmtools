# This is a workaround script to get docker versions working with pip versions and to automate build of those images
import os
import subprocess
import sys

version = open('VERSION').read().strip()
if '+nightly' in version:
    version = version.replace('+nightly', '.nightly')
cmd = ['docker', 'push', f'idm-docker-staging.packages.idmod.org/idmtools_local_workers:{version}']
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
sys.exit(p.returncode)
