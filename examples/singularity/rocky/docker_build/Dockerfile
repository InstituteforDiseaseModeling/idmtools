FROM rockylinux/rockylinux:8.5

RUN yum -y install rpm dnf-plugins-core \
 && yum -y update \
 && yum -y install \
    python39-devel \
    mpich-devel \
    sqlite-devel \
    boost-devel \
    git \
    vim \
    snappy
RUN yum -y group install "Development Tools" \
 && yum clean all

RUN pip3 install --upgrade pip \
 && python3 -m pip install scons pytest \
 && python3 -m pip install emod-api --extra-index-url https://packages.idmod.org/api/pypi/pypi-production/simple

RUN export PATH=$PATH:/usr/lib64/mpich/bin \
 && export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/mpich/lib