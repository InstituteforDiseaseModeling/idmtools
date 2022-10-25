FROM ubuntu:20.04

# Install dependencies
RUN apt-get update

ENV PYTHONPATH=./Assets/:./Assets/site-packages/:.
# set the timezone - do this before installing python
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

# install Python3
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-dev
RUN apt-get install -y python3-setuptools

# r packages to support analysis in R
RUN apt-get install -y xz-utils llvm r-base \
    # clean up temporary data
    && mkdir -p /root/.pip

#    && apt-get clean && \     <--- We do this at the end of this file
#    mkdir -p /root/.pip && \
#    rm -rf /var/lib/apt/lists/*    <--- We do this at the end of this file

# add requirements file
ADD requirements.txt /tmp/
# set default index to IDM Pip Prod(Caching and internal packages IDMTools may depend on like pyComps
ADD pip.conf /etc/pip.conf

COPY .depends/* /tmp/

RUN pip3 install -U pip && \
    pip install pygit2

RUN bash -c "pip3 install /tmp/*.gz --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple"

# make the PIP index configurable so we can build against staging, production, or a local PyPI server
ARG SSMT_VERSION

# Install the packages
RUN pip3 install --upgrade pip --index-url=https://pypi.python.org/simple && \
    pip3 install dataclasses && \
    pip3 install -r /tmp/requirements.txt && \
    rm -rf /root/.cache
    # To make this effective, we need to collapse this to one layer....... so don't do it for now
    # remove stuff we needed for pip but don't want in our final image
    # apt-get remove build-essential

RUN apt-get clean && rm -rf /var/lib/apt/lists/*