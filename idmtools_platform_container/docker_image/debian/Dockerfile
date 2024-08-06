FROM debian:12.6
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN set -x && \
    apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        mpich \
        wget \
        nano \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Update the system
RUN apt-get clean

RUN mkdir /root/.pip
# Copy the pip configuration file
COPY pip.conf /root/.pip

# Set up a virtual environment
RUN python3 -m venv /pyenv
ENV PATH="/pyenv/bin:$PATH"

RUN pip3 install --upgrade pip setuptools
# Add the requirements file
ADD requirements.txt /tmp/
# Install the packages
RUN pip3 install -r /tmp/requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python

ARG CONTAINER_VERSION

ENV LD_LIBRARY_PATH /usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH}


