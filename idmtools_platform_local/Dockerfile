FROM python:3.8.11-buster
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
    && curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - \
    && add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/debian \
    $(lsb_release -cs) \
    stable" \
    && wget -O- http://neuro.debian.net/lists/buster.us-nh.full | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list \
    && apt-key adv --recv-keys --keyserver hkps://keyserver.ubuntu.com 0xA5D32F012649A5A9 \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli nginx singularity-container \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -s /bin/bash idmtools \
    && echo "idmtools:idmtools" | chpasswd \
    && mkdir -p /home/idmtools /data /app/log /app/tmp/client_body \
        /app/tmp/fastcgi_temp /app/tmp/proxy_temp /app/tmp/scgi_temp /app/tmp/uwsgi_temp \
    && chown -R idmtools:idmtools /home/idmtools /data /app \
    && addgroup idmtools staff \
    # create docker group and idmtools to it so they can use it
    # without prompts
    && addgroup --gid 999 docker \
    && usermod -a -G docker idmtools \
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
ADD docker_scripts/cont-init.d /etc/cont-init.d
# Our service scripts
ADD docker_scripts/services /etc/services.d
COPY docker_scripts/uwsgi.ini docker_scripts/nginx.conf /app/

# Define a workdirectory
WORKDIR /app
ENV PYTHONPATH=/app:${PYTHONPATH}


#TODO: Move the actual package to artifactory and install from there. It would simpify the environmetn quite a bit

# make it where we can specifiy our dependent packages at build time
COPY .depends/* /tmp/
RUN python -m pip install --upgrade pip
RUN bash -c "pip install /tmp/*.gz --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple"
# Install requirements first to reduce build cache misses
ADD requirements.txt ui_requirements.txt workers_requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple && \
        pip install -r /tmp/ui_requirements.txt --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple && \
        pip install -r /tmp/workers_requirements.txt --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
# Run the setup instal before copying rest of package. This will increase cache hits during docker builds
# as we will only rebuild if any of the docker_scripts, setup.py, readme.md, and requirements.txt change
# which should happen infrequently(or less so than library code)
COPY dist/idmtools_platform_local*.tar.gz /tmp/
RUN find /tmp -name idmtools_platform_local*.tar.gz -exec pip install {}[workers,ui,server] --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple \; && \
    rm -rf /root/.cache
ADD idmtools_platform_local/internals/ui/static /app/html
CMD ["/init"]