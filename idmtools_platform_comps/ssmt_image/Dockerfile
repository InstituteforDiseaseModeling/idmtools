## Start from the official Ubuntu 18.4 image
## TODO Change to COMPS base image tag once image is in artifactory
FROM ubuntu:18.04

MAINTAINER COMPS Team version: 1.0
RUN apt-get update
RUN apt-get install -y net-tools &&  apt-get install -y iputils-ping
RUN apt-get install -y telnet
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get install -y vim
RUN apt-get install -y dos2unix
RUN apt-get install -y dnsutils
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get install -y build-essential
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools
RUN apt-get install -y python3-tk
RUN cd /usr/local && pip3 install pyCOMPS -i https://packages.idmod.org/api/pypi/pypi-production/simple
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
COPY bootstrap.sh /root/bootstrap.sh
CMD source /root/bootstrap.sh

## Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN apt-get clean && rm -rf /var/lib/apt/lists/*
COPY bootstrap.sh /root/bootstrap.sh
CMD source /root/bootstrap.sh

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    xz-utils \
    llvm \
    # r packages to support analysis in R
    r-base \
    # clean up temporary data
    && apt-get clean && \
    mkdir -p /root/.pip && \
    rm -rf /var/lib/apt/lists/*


# add requirements file
ADD requirements.txt /tmp/
# set default index to IDM Pip Prod(Caching and internal packages IDMTools may depend on like pyComps
ADD pip.conf /etc/pip.conf

# make the PIP index configurable so we can build against staging, production, or a local PyPI server
ARG PYPIURL=https://packages.idmod.org/api/pypi/pypi-staging/simple
ARG PYPIHOST=packages.idmod.org
ARG SSMT_VERSION

# Install the packages
RUN pip3 install --upgrade pip --index-url=https://pypi.python.org/simple && \
    pip3 -v install -r /tmp/requirements.txt --index-url=${PYPIURL} --trusted-host ${PYPIHOST} && \
    rm -rf /root/.cache
    # To make this effective, we need to collapse this to one layer....... so don't do it for now
    # remove stuff we needed for pip but don't want in our final image
    # apt-get remove build-essential

