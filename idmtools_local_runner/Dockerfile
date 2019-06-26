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
      && (cd tmp && curl -LO https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz) \
      ## and set it up at root
      && tar xzf /tmp/s6-overlay-amd64.tar.gz -C / \
      && rm -rf /tmp/s6-overlay-amd64.tar.gz

# Our script that does smart user mapping
COPY docker_scripts /etc/cont-init.d/01-user_conf.sh
COPY docker_scripts /etc/services.d/idmtools_workers/run

WORKDIR /app
ENV PYTHONPATH=/app:${PYTHONPATH}

ADD idmtools_local /tmp/idmtools_local
COPY README.md setup.py requirements.txt /tmp/
RUN cd /tmp && pip install -e .

CMD ["/init"]