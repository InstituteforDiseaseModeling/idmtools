#FROM docker-production.packages.idmod.org/dtk-rocky-buildenv:0.2-dev
# Replace the following lines with above line after the offical image is available
#############################################################
FROM rockylinux:9.2
ENV TZ=America/LosAngeles DEBIAN_FRONTEND=noninteractive
ENV GNUMAKEFLAGS=-j4

RUN yum -y install rpm dnf-plugins-core \
 && yum -y update \
 && dnf -y install \
    python3 \
    python3-devel \
    snappy \
    mpich \
    sudo \
    epel-release \
    git \
    wget \
    nano

RUN yum -y update
RUN yum -y group install "Development Tools" \
 && yum clean all

RUN python3 -m pip install pip --upgrade
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir /root/.pip
COPY pip.conf /root/.pip
# RUN dnf install -y R
ENV PATH ${PATH}:/usr/lib64/mpich/bin
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/lib64/mpich/lib

#############################################################
RUN dnf -y install dos2unix

# Add the requirements file
ADD requirements.txt /tmp/

# make the PIP index configurable so we can build against staging, production, or a local PyPI server
ARG CONTAINER_VERSION

# Install the packages
RUN bash -c "pip3 install -r /tmp/requirements.txt"

