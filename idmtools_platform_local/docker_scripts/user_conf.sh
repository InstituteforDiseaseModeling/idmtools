#!/usr/bin/with-contenv bash

## Set defaults for environmental variables in case they are undefined
USER=${USER:=idmtools}
PASSWORD=${PASSWORD:=idmtools}
USER_DATA=
# load the user and group ids
IFS=':' read -r -a id_array <<< "${CURRENT_UID:=1000:1000}"

USERID=${id_array[0]}
GROUPID=${id_array[1]}
ROOT=${ROOT:=FALSE}
UMASK=${UMASK:=022}

echo "$USER"

if [[ "$USERID" -ne 1000 ]]
## Configure user with a different USERID if requested.
  then
    echo "deleting user idmtools"
    userdel idmtools
    echo "creating new $USER with UID $USERID"
    useradd -m $USER -u $USERID
    mkdir /home/$USER
    chown -R $USER /home/$USER /data /app
    usermod -a -G staff $USER
elif [[ "$USER" != "idmtools" ]]
  then
    echo "Renaming idmtools to $USER"
    ## cannot move home folder when it's a shared volume, have to copy and change permissions instead
    cp -r /home/idmtools /home/$USER
    ## RENAME the user
    usermod -l $USER -d /home/$USER idmtools
    groupmod -n $USER idmtools
    usermod -a -G staff $USER
    chown -R $USER:$USER /home/$USER /data /app
    echo "USER is now $USER"
else
    echo "Ensuring proper permissions on data directories"
    chown -R $USER:$USER /home/$USER /data /app
fi

if [[ "$GROUPID" -ne 1000 ]]
## Configure the primary GID (whether rstudio or $USER) with a different GROUPID if requested.
  then
    echo "Modifying primary group $(id $USER -g -n)"
    groupmod -g $GROUPID $(id $USER -g -n)
    echo "Primary group ID is now custom_group $GROUPID"
fi

## Add a password to user
echo "$USER:$PASSWORD" | chpasswd

# Use Env flag to know if user should be added to sudoers
if [[ ${ROOT,,} == "true" ]]
  then
    adduser $USER sudo && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
    echo "$USER added to sudoers"
fi

# Check for dev build. If this exists we want to install fresh copies of the packages
if [[ -d "/dev_build" ]];
  then
    cd /dev_build && python dev_scripts/bootstrap.py
fi