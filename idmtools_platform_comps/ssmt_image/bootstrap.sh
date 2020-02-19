#!/bin/bash
#
echo "---> bootstrap.sh: Starting"
cd $COMPS_WORKING_DIR
echo "---> bootstrap.sh: Environment variables:"
env
echo "---> bootstrap.sh: End of environment variables."

if [[ $COMPS_WORKING_DIR != $PWD ]]; then
	exit 254
fi
EXITCODE=255
if [[ -z "${COMPS_STARTUP_CMD// }" ]]; then
	echo "---> bootstrap.sh: COMPS_STARTUP_CMD environment variable not specified."
else
   echo Executing system command: $COMPS_STARTUP_CMD
   eval "$COMPS_STARTUP_CMD"
	EXITCODE=$?
fi

if [[ -z "${COMPS_USER_CMD// }" ]]; then
	echo "---> bootstrap.sh: COMPS_USER_CMD environment variable not specified."
else
   echo Executing user command: $COMPS_USER_CMD
   eval "$COMPS_USER_CMD"
	EXITCODE=$?
fi

echo "---> bootstrap.sh: Finished ($EXITCODE)"
exit $EXITCODE
