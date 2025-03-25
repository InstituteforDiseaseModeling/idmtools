#!/bin/bash
# Ensure system packages are updated
sudo apt update && sudo apt upgrade -y

# Install extra system dependencies if needed
sudo apt install -y build-essential curl git unzip zip

# Install additional Python packages
pip install --upgrade pip
pip install numpy pandas matplotlib seaborn jupyterlab ipykernel


# Verify Docker access
sudo usermod -aG docker $USER
sudo chown root:docker /var/run/docker.sock
sudo chmod 666 /var/run/docker.sock
docker --version
sudo chown -R codespace:codespace /workspaces/idmtools

# install idmtools
pip install idmtools[full] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
pip install idmtools-test --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
