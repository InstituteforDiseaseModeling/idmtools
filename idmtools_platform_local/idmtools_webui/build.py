#!/usr/bin/env python

import os
import sys

if os.name == 'nt':
    uid = "1000:1000"
else:
    uid = f'{os.getuid()}:{os.getgid()}'
os.system('docker-compose -f build.yml build')
cmd = f'docker-compose -f build.yml run --rm -e "CURRENT_UID={uid}" buildenv "yarn install && npm run build"'
print(cmd)
sys.exit(os.system(cmd))
