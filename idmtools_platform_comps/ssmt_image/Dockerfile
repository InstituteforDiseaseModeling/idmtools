## Start from the official Ubuntu 18.4 image
FROM ubuntu:18.04

## Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Install dependencies
RUN apt-get update && \
    apt-get install -y \
    xz-utils \
    llvm \
    # r packages to support analysis in R
    r-base
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

# Install the packages
RUN pip3 install --upgrade pip --index-url=https://pypi.python.org/simple && \
    pip3 -v install -r /tmp/requirements.txt --index-url=${PYPIURL} --trusted-host ${PYPIHOST} && \
    rm -rf /root/.cache
    # To make this effective, we need to collapse this to one layer....... so don't do it for now
    # remove stuff we needed for pip but don't want in our final image
    # apt-get remove build-essential