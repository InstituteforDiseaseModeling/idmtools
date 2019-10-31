FROM r-base:3.6.1

ARG S6_VERSION
ENV S6_VERSION=${S6_VERSION:-v1.22.1.0} \
    S6_BEHAVIOUR_IF_STAGE2_FAILS=2 \
    DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    # required by devtools and ggmap
    libssl-dev libcurl4-gnutls-dev libxml2-dev libgit2-dev \
    sudo apt-utils curl gzip file python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # change docker group(not sure why it is even part of r-base)
    && usermod -u 999 docker \
    && groupmod -g 999 docker \
    && (find / -group 1000 -exec chgrp -h docker {} \; || true) \
    && (find / -user 1000 -exec chown -h docker {} \; || true) \
    && useradd -s /bin/bash idmtools \
    && echo "idmtools:idmtools" | chpasswd \
    && mkdir /home/idmtools /data /app \
    && chown -R idmtools:idmtools /home/idmtools /data /app \
    # We add the s6 overlay kit which helps us manager permissions
    # multiple applications, etc within an image
    # overall it make management of our final image a bit easier
    # see https://github.com/just-containers/s6-overlay
    && (cd tmp && curl -LO https://github.com/just-containers/s6-overlay/releases/download/${S6_VERSION}/s6-overlay-amd64.tar.gz) \
    ## and set it up at root
    && tar xzf /tmp/s6-overlay-amd64.tar.gz -C / \
    && rm -rf /tmp/s6-overlay-amd64.tar.gz

# Set default make to parallel build
ARG WORKERS=2
ENV MAKE="make -j${WORKERS}"
# install dev tools.
# this increases the final build size but also gives use the ability to install specific versions of packages
# which is overall more stable
RUN Rscript -e "install.packages('devtools')"
# For a stable environment, use specific versions of packages we use within our projectt
RUN Rscript -e "devtools::install_version('argparse', version = '2.0.1')" && \
    Rscript -e "devtools::install_version('deSolve', version = '1.24')"

# Our script that does smart user mapping
COPY user_conf.sh /etc/cont-init.d/01-user_conf.sh
COPY user_init.sh /

WORKDIR /app
COPY user_conf.sh /app
RUN chmod +x /user_init.sh /app/user_conf.sh
COPY model.R example.json /app/
ENTRYPOINT ["/user_init.sh"]