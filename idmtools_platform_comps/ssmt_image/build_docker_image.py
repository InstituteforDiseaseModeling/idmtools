####
# This script is currently a workaround so that we can use bump2version with docker since the nightly versions
# don't work with docker registry
import os
import subprocess
import sys
from urllib.parse import urlparse

version = open('../VERSION').read().strip()
if '+nightly' in version:
    version = version.replace('+nightly', '.nightly')
print(f'PIP URL: {sys.argv[1]}')
uri = urlparse(sys.argv[1])

cmd = ['docker', 'build', '--network=host', '--build-arg', f'PYPIURL={sys.argv[1]}', '--build-arg',
       f'PYPIHOST={uri.hostname}', '--tag',
       f'idm-docker-staging.packages.idmod.org/idmtools_comps_ssmt_worker:{version}', '.']
if len(sys.argv) == 3 and sys.argv[2] == "no-cache":
    cmd.insert(2, "--no-cache")
print(f'Running: {" ".join(cmd)}')
p = subprocess.Popen(" ".join(cmd), cwd=os.path.abspath(os.path.dirname(__file__)), shell=True)
p.wait()
sys.exit(p.returncode)
