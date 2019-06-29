FROM python:3.7.2

ARG S6_VERSION
ENV S6_VERSION=${S6_VERSION:-v1.21.7.0} \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    DEBIAN_FRONTEND=noninteractive

# Install sudo. Useful in debugging/development in combination with -e ROOT=true
RUN apt-get update \
    && apt-get install -y --no-install-recommends sudo \
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
ADD idmtools_local /tmp/idmtools_local
COPY README.md setup.py requirements.txt /tmp/
# We install the package directly here so the source is within the final image
# This will allow users later to download the image without needing to build it
# Also we specially use the internal pypy for ALL packages to take advantage of package caching

RUN cd /tmp && \
    pip install .[workers,ui] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple && \
    # cleanup pip cache and tmp
    rm -rf /root/.cache && \
    rm -rf /tmp/*

CMD ["/init"]