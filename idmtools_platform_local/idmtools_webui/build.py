#!/usr/bin/env python
"""Build command for our webui."""
import os
import sys

if os.name == 'nt':
    uid = "1000:1000"
else:
    uid = f'{os.getuid()}:{os.getgid()}'

if len(sys.argv) > 1 and sys.argv[1] == "clean":
    print('Cleaning node build cache')
    os.system('docker-compose -f build.yml down -v')
elif len(sys.argv) > 1 and sys.argv[1] == "upgrade":
    os.system('docker-compose -f build.yml build')
    cmd = f'docker-compose -f build.yml run --rm -e "CURRENT_UID={uid}" buildenv "yarn upgrade"'
    print(cmd)
    sys.exit(os.system(cmd))
else:
    os.system('docker-compose -f build.yml build')
    cmd = f'docker-compose -f build.yml run --rm -e "CURRENT_UID={uid}" buildenv "yarn install && npm run build"'
    print(cmd)
    sys.exit(os.system(cmd))
