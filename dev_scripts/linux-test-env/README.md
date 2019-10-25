This environment is intended for Windows developers to test idmtools on linux.
Before use, be sure you have ran 
`make setup-dev`
This is required to create the worker containers used by tasks internally

To use, run 
`docker-compose run linuxtst` 
from this directory. It will provide you with a Linux terminal you can then use for testing. Be sure to also do the following before running tests:
- docker login idm-docker-staging.packages.idmod.org
- python dev_scripts/create_auth_token_args.py


In addition, the idmtools has password-less sudo access so you can install any needed packages.
Remember to run `sudo apt update` first
# TODO
Support docker builds within container. We need to detect the gateway address
