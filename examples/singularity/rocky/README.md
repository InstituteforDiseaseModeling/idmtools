<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Push sif to artifactory:](#push-sif-to-artifactory)
- [Download from artifactory:](#download-from-artifactory)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Push sif to artifactory:
curl -u idm_bamboo_user@idmod.org:apikey -X PUT https://packages.idmod.org/artifactory/idm-docker-staging/idmtools/rocky_mpi/dtk_run_rocky_py39.sif -T ./dtk_run_rocky_py39.sif

# Download from artifactory:
curl -u idm_bamboo_user@idmod.org:apikey https://packages.idmod.org:443/artifactory/idm-docker-staging/idmtools/rocky_mpi/dtk_run_rocky_py39.sif -o dtk_run_rocky_py39.sif
