# FROM docker-production.packages.idmod.org/dtk-rocky-buildenv:0.2-dev
# Replace the following lines with above line after the offical image is available
#############################################################
FROM rockylinux:9.2
# Set the timezone and the frontend
ENV TZ=UTC DEBIAN_FRONTEND=noninteractive
# To suppress warning without altering the installation when pip install with root user
ENV PIP_ROOT_USER_ACTION=ignore
# Install the necessary packages
RUN yum -y install rpm dnf-plugins-core \
 && yum -y update \
 && dnf -y install \
    python3 \
    python3-devel \
    mpich \
    snappy \
    glibc-devel \
    epel-release \
    wget \
    nano


# Update the system
RUN yum clean all

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone # This is for setting up the timezone

# Install pip
RUN python3 -m pip install pip --upgrade
# Create a symbolic link to python3
RUN ln -s /usr/bin/python3 /usr/bin/python
# Create a directory for pip configurations
RUN mkdir /root/.pip
# Copy the pip configuration file
COPY pip.conf /root/.pip

# Set the path and library path
ENV PATH ${PATH}:/usr/lib64/mpich/bin
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:/usr/lib64/mpich/lib

# Add the requirements file
ADD requirements.txt /tmp/

# make the PIP index configurable so we can build against staging, production, or a local PyPI server
ARG CONTAINER_VERSION

# Install emod-api packages
RUN bash -c "pip3 install -r /tmp/requirements.txt"


