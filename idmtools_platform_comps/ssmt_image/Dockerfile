## Start from the official Ubuntu 18.4 image
FROM ubuntu:18.04

## Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    build-essential \
    curl \
    pkg-config \
    python3-dev \
    python3-pip \
    unzip \
    software-properties-common \
    llvm \
    r-base
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \



ADD requirements.txt /tmp/


ARG PYPIURL=https://packages.idmod.org/api/pypi/pypi-staging/simple
ARG PYPIHOST=packages.idmod.org

RUN pip3 install --upgrade pip && \
    pip3 install -r /tmp/requirements.txt --extra-index-url=${PYPIURL} --trusted-host ${PYPIHOST} && \
    rm -rf /root/.cache