#!/usr/bin/with-contenv bash

## Set defaults for environmental variables in case they are undefined
USER=${USER:=idmtools}
PASSWORD=${PASSWORD:=idmtools}
IDMTOOLS_ID=$(id -u idmtools)
IDMTOOLS_GROUP=$(id -g idmtools)
USER_DATA=
# load the user and group ids
IFS=':' read -r -a id_array <<< "${CURRENT_UID:=$IDMTOOLS_ID:$IDMTOOLS_GROUP}"

USERID=${id_array[0]}
GROUPID=${id_array[1]}
ROOT=${ROOT:=FALSE}
UMASK=${UMASK:=022}

# Get the owner of docker socket and the container docker id
DOCKER_SOCKET_GROUP=$(stat -c '%g' /var/run/docker.sock)
DOCKER_GID=$(cut -d: -f3 < <(getent group docker))

if [[ "$USERID" -ne "$IDMTOOLS_ID" ]]
## Configure user with a different USERID if requested.
  then
    echo "deleting user idmtools"
    userdel idmtools
    echo "creating new $USER with UID $USERID"
    useradd -m $USER -u $USERID
    [[ -d /home/$USER ]] || mkdir /home/$USER
    chown -R $USER /home/$USER /data /app
    usermod -a -G staff $USER
    # Adding idmtools to docker group
    usermod -a -G docker idmtools
elif [[ "$USER" != "idmtools" ]]
  then
    echo "Renaming idmtools to $USER"
    ## cannot move home folder when it's a shared volume, have to copy and change permissions instead
    cp -r /home/idmtools /home/$USER
    ## RENAME the user
    usermod -l $USER -d /home/$USER idmtools
    groupmod -n $USER idmtools
    usermod -a -G staff $USER
    # Adding idmtools to docker group
    usermod -a -G docker idmtools
    chown -R $USER:$USER /home/$USER /data /app
    echo "USER is now $USER"
else
    echo "Ensuring proper permissions on data directories"
    chown -R $USER:$USER /home/$USER /data /app
fi

if [[ "$GROUPID" -ne "$IDMTOOLS_GROUP" ]]
## Configure the primary GID (whether rstudio or $USER) with a different GROUPID if requested.
  then
    echo "Modifying primary group $(id $USER -g -n)"
    groupmod -g $GROUPID $(id $USER -g -n)
    echo "Primary group ID is now custom_group $GROUPID"
fi

## Ensure the docker group matches the host docker group id. This allows the idmtools users to run docker commands
if [[ "$DOCKER_GID" -ne "$DOCKER_SOCKET_GROUP" ]]; then
    if [[ "$DOCKER_SOCKET_GROUP" -eq 0 ]]; then
        echo "Changing group on docker socket to docker from root group"
        chgrp  docker /var/run/docker.sock
    elif [[ "${DOCKER_SOCKET_GROUP}" -eq "${USERID}" ]]; then
        echo "Docker group id cannot be the same id as the run user"
        exit -1
    else
        echo "Recreating Docker GROUP with GID ${DOCKER_SOCKET_GROUP}"
        groupdel docker
        addgroup --gid ${DOCKER_SOCKET_GROUP} docker
        # Adding idmtools to docker group
        usermod -a -G docker idmtools
    fi

fi

## Add a password to user
echo "$USER:$PASSWORD" | chpasswd

## Add user to sudo group to allow advanced changes/development tools for environment
if [[ ${ROOT,,} == "true" ]]
  then
    adduser $USER sudo && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
    echo "$USER added to sudoers"
fi

## Check for dev build. If this exists we want to install fresh copies of the packages
if [[ -d "/dev_build" ]];
  then
    cd /dev_build && python dev_scripts/bootstrap.py
fi