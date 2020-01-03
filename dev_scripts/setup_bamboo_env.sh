#!/usr/bin/env bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# Takes in the username and password for packages.idmod.org and creates a pypirc in users home directory

echo "Setting up pypirc"
cp "${SRC_DIR}/.pypirc" ~/.pypirc
echo "Replacing <username> with ${bamboo_UserArtifactory}"
sed -i "s|<username>|${bamboo_UserArtifactory}|" ~/.pypirc
# we could end up with characters in our password that conflict with our sed replacement
# instead of trying to escape, which bash is not good at, we just check for a series of characters
# presence and then use an appriote sed expression
if [[ $bamboo_PasswordArtifactory == *"|"* ]]; then
  sed -i "s/<password>/${bamboo_PasswordArtifactory}/" ~/.pypirc
else
  sed -i "s|<password>|${bamboo_PasswordArtifactory}|" ~/.pypirc
fi
