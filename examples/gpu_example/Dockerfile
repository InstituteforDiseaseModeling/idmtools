# Selected through https://rapids.ai/start.html
FROM rapidsai/rapidsai-dev:0.10-cuda9.2-devel-ubuntu18.04-py3.7

ARG S6_VERSION
ENV S6_VERSION=${S6_VERSION:-v1.21.7.0} \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    DEBIAN_FRONTEND=noninteractive

# Install sudo, python3 and pip
# Also setup our user accounts and working directories
# Lastely, we setup s6 overlay to manage running environment
RUN apt-get update \
    && apt-get install -y --no-install-recommends sudo apt-utils curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -s /bin/bash idmtools \
    && echo "idmtools:idmtools" | chpasswd \
    && mkdir /home/idmtools /data /app \
    && chown -R idmtools:idmtools /home/idmtools /data /app \
    && addgroup idmtools staff \
    # We add the s6 overlay kit which helps us manager permissions
    # multiple applications, etc within an image
    # overall it make management of our final image a bit easier
    # see https://github.com/just-containers/s6-overlay
    # We should probably move to a newer version eventually
    && (cd /tmp && curl -LO https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz) \
    ## and set it up at root
    && tar xzf /tmp/s6-overlay-amd64.tar.gz -C / \
    && rm -rf /tmp/s6-overlay-amd64.tar.gz

# Our script that does smart user mapping
COPY user_conf.sh /etc/cont-init.d/01-user_conf.sh

WORKDIR /app
# Add requriements first and run setup to optimize use of docker cache
ADD requirements.txt /app
RUN pip install -r ./requirements.txt
ADD gpu_model.py /app
CMD python3 /app/gpu_model.py