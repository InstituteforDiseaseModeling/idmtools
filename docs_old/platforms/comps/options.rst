=========================
Configuration and options
=========================
|IT_s| supports the |COMPS_s| platform options.
The following lists some of the COMPSPlatform options that are used when making calls to
:py:class:`idmtools_platform_comps.comps_platform.COMPSPlatform`:


*  endpoint (str, optional): URL of the COMPS endpoint to use. Default is 'https://comps.idmod.org'
*  environment (str, optional):  Name of the COMPS environment to target, Default is Calculon, Options are Calculon, IDMcloud, SlurmStage, Cumulus, etc
*  priority (str, optional): Priority of the job. Default is 'Lowest'. Options are Lowest, BelowNormal, Normal, AboveNormal, Highest
*  node_group (str, optional): node group to target. Default is None. Options are 'idm_abcd', 'idm_ab', idm_cd', 'idm_a', 'idm_b', 'idm_c', 'idm_d', 'idm_48cores'
*  num_retries (int, optional): How retries if the simulation fails, Default is 0, max is 10
*  num_cores (int, optional): How many cores per simulation. Default is 1, max is 32
*  max_workers (int, optional): The number of processes to spawn locally. Defaults to 16, min is 1, max is 32
*  batch_size (int, optional): How many simulations per batch. Default is 10, min is 1 and max is 100
*  exclusive (bool, optional): Enable exclusive mode? (one simulation per node on the cluster). Default is False
*  docker_image (str, optional): Docker image to use for the simulation. Default is None