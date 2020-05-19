import os
import sys
from getpass import getpass

username = os.getenv("DOCKER_USERNAME", input("Docker Username: "))
password = os.getenv("DOCKER_PASSWORD", getpass(prompt="Password: ", stream=sys.stdout))
print('Performing logins')
ret = os.system(f'docker login --username "{username}" --password "{password}" idm-docker-staging.packages.idmod.org')
ret2 = os.system(f'docker login --username "{username}" --password "{password}" docker-staging.packages.idmod.org')
sys.exit(0 if ret == 0 and ret2 == 0 else -1)
