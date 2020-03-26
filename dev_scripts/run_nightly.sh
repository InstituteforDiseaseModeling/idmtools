#!/usr/bin/env bash

SRC_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VIRTUALENV_DIR="$(mktemp -d)"

echo "env" $VIRTUALENV_DIR
trap 'rm -r "${VIRTUALENV_DIR}"' EXIT
python3 -m venv "${VIRTUALENV_DIR}"
source "${VIRTUALENV_DIR}/bin/activate"

echo "install required libraries for packaging"
pip install py-make twine bump2version twine


echo "Setting up pypirc"
cp "${SRC_DIR}/.pypirc" ~/.pypirc
cat ~/.pypirc
echo "Replacing <username> with ${bamboo_UserArtifactory}"
sed -i "s|<username>|${bamboo_UserArtifactory}|" ~/.pypirc
# we could end up with characters in our password that conflict with our sed replacement
# instead of trying to escape, which bash is not good at, we just check for a series of characters
# presence and then use an appriote sed expression
if [[ "$bamboo_PasswordArtifactory" == *"|"* ]]; then
  sed -i "s/<password>/${bamboo_PasswordArtifactory}/" ~/.pypirc
else
  sed -i "s|<password>|${bamboo_PasswordArtifactory}|" ~/.pypirc
fi
cat ~/.pypirc

export TWINE_USERNAME="${bamboo_UserArtifactory}"
export TWINE_PASSWORD="${bamboo_PasswordArtifactory}"
export TWINE_NON_INTERACTIVE="True"
echo "Login to docker"
docker login idm-docker-staging.packages.idmod.org -u "${bamboo_UserArtifactory}" -p "${bamboo_PasswordArtifactory}"

export STAGING_PIP_URL=https://$(urlencode ${bamboo_UserArtifactory}):$(urlencode ${bamboo_PasswordArtifactory})@packages.idmod.org/api/pypi/idm-pypi-staging/simple
echo "Release to staging"
pymake release-staging

echo "deactivate..."
deactivate