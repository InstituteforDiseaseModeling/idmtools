#!/usr/bin/env python

import os
import sys

if os.name == 'nt':
    uid = "1000:1000"
else:
    uid = f'{os.getuid()}:{os.getgid()}'
cmd=f'docker-compose -f build.yml  run --rm -e "CURRENT_UID={uid}" buildenv su - idmtools ' \
    f'-c "cd /app && yarn install && npm run build"'
print(cmd)
sys.exit(os.system(cmd))
