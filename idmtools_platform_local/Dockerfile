FROM python:3.7.4

ARG S6_VERSION
ENV S6_VERSION=${S6_VERSION:-v1.21.7.0} \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    DEBIAN_FRONTEND=noninteractive

# Install sudo. Useful in debugging/development in combination with -e ROOT=true
RUN apt-get update \
    # setup sudo and packages allowing us to install docker repo
    && apt-get install -y --no-install-recommends sudo apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common \
    # install docker-cli
    && curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
    && add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) \
    stable"
    && apt-get update
    && apt-get install -y --no-install-recommends docker-ce-cli
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

## Need to configure non-root user
RUN useradd -s /bin/bash idmtools \
      && echo "idmtools:idmtools" | chpasswd \
      && mkdir /home/idmtools /data /app \
      && chown -R idmtools:idmtools /home/idmtools /data /app \
      && addgroup idmtools staff \
      # We add the s6 overlay kit which helps us manager permissions
      # multiple applications, etc within an image
      # overall it make management of our final image a bit easier
      # see https://github.com/just-containers/s6-overlay
      # We should probably move to a newer version eventually
      && (cd tmp && curl -LO https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz) \
      ## and set it up at root
      && tar xzf /tmp/s6-overlay-amd64.tar.gz -C / \
      && rm -rf /tmp/s6-overlay-amd64.tar.gz

# Our script that does smart user mapping
COPY docker_scripts/user_conf.sh /etc/cont-init.d/01-user_conf.sh
# Our service scripts
COPY docker_scripts/start_workers.sh /etc/services.d/idmtools_workers/run
COPY docker_scripts/start_ui.sh /etc/services.d/idmtools_ui/run

# Define a workdirectory
WORKDIR /app
ENV PYTHONPATH=/app:${PYTHONPATH}

#TODO: Move the actual package to artifactory and install from there. It would simpify the environmetn quite a bit

COPY README.md setup.py requirements.txt /tmp/
# Run the setup instal before copying rest of package. This will increase cache hits during docker builds
# as we will only rebuild if any of the docker_scripts, setup.py, readme.md, and requirements.txt change
# which should happen infrequently(or less so than library code)
RUN cd /tmp && pip install -e .[workers,ui]
ADD idmtools_platform_local /tmp/idmtools_local
# We install the package directly here so the source is within the final image
# This will allow users later to download the image without needing to build it
# Also we specially use the internal pypy for ALL packages to take advantage of package caching

RUN cd /tmp && \
    # we need install the full version of local_runner as it is both a Client and Server package
    # to do this, we specify we want the workers and the UI
    pip install .[workers,ui] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple && \
    # cleanup pip cache and tmp
    rm -rf /root/.cache && \
    rm -rf /tmp/*

CMD ["/init"]