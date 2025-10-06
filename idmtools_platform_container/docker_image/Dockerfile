# FROM docker-production.packages.idmod.org/dtk-rocky-buildenv:0.2-dev
# Replace the following lines with above line after the offical image is available
#############################################################
FROM rockylinux:9.2

ENV TZ=UTC \
    DEBIAN_FRONTEND=noninteractive \
    PIP_ROOT_USER_ACTION=ignore \
    PATH="${PATH}:/usr/lib64/mpich/bin" \
    LD_LIBRARY_PATH="/usr/lib64/mpich/lib:${LD_LIBRARY_PATH:-}"

# Install the necessary packages
RUN set -eux; \
    dnf -y clean all && \
    dnf -y install dnf-plugins-core epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf -y update && \
    dnf -y install \
        python3 \
        python3-devel \
        mpich \
        snappy \
        glibc-devel \
        wget \
        nano && \
    dnf clean all

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone # This is for setting up the timezone

# Install pip
RUN python3 -m pip install pip --upgrade
# Create a symbolic link to python3
RUN ln -s /usr/bin/python3 /usr/bin/python
# Create a directory for pip configurations
RUN mkdir /root/.pip
# Copy the pip configuration file
COPY pip.conf /root/.pip

# Add the requirements file
ADD requirements.txt /tmp/

# make the PIP index configurable so we can build against staging, production, or a local PyPI server
ARG CONTAINER_VERSION

# Install the packages
RUN pip3 install -r /tmp/requirements.txt

# -----------------------------
# ADD ENTRYPOINT SCRIPT FOR NON-ROOT USER SUPPORT
# -----------------------------
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["bash"]