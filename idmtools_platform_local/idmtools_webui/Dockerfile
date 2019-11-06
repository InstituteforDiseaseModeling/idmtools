FROM node:10.16.3
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && userdel node \
    && useradd -s /bin/bash idmtools \
    && echo "idmtools:idmtools" | chpasswd \
    && mkdir /home/idmtools /app \
    && chown -R idmtools:idmtools /home/idmtools /app \
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

COPY docker_scripts/user_conf.sh /etc/cont-init.d/01-user_conf.sh
ADD package.json yarn.lock /app/
ADD docker_scripts/user_init.sh /
RUN chmod +x /user_init.sh
ENTRYPOINT ["/user_init.sh "]