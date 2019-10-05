FROM python:3.7
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
    && curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add - \
    && add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) \
    stable" \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli virtualenvwrapper \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -s /bin/bash idmtools \
    && groupadd docker \
    && usermod -a -G docker idmtools \
    && echo "idmtools:idmtools" | chpasswd \
    && mkdir /home/idmtools /idmtools \
    && chown -R idmtools:idmtools /home/idmtools /idmtools \
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

COPY .bash_profile /home/idmtools/
# Our script that does smart user mapping
COPY user_conf.sh /etc/cont-init.d/01-user_conf.sh

ENTRYPOINT ["/init"]
CMD su - idmtools