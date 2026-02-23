.. _changelog-2.0.2:


=====
2.0.2
=====

Bugs
----
* `#2391 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2391>`_ - Random fail with large number of simulations with NoneType of platform
* `#2393 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2393>`_ - Calibra may fail with ContainerPlatform
* `#2395 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2395>`_ - Slurm: Do not need to delete suite if job_directory is not exist or suite not exist anymore
* `#2399 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2399>`_ - docker container can become unusable in linux

Documentation
-------------
* `#2386 <https://github.com/InstituteforDiseaseModeling/idmtools/pull/2386>`_ - jupyter lab version fix

Feature Request
---------------
* `#2377 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2377>`_ - Need to change github actions to only build container docker image when there are related changes
* `#2172 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2172>`_ - Adjust the default 'max_running_jobs' in SlurmPlatform
* `#2379 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2379>`_ - Container Platform needs to support multiple processes
* `#2396 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2396>`_ - Assets duplication

Platforms
---------
* `#2388 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2388>`_ - Performance issue with get_item in slurm platform when there are lot of items in job directory
* `#2389 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2389>`_ - Performance issue with get_item in container platform when there are lot of items in job directory
* `#2247 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2247>`_ - Investigation: run each simulation on SLURM with multi cores

Release/Packaging
-----------------
* `#2400 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2400>`_ - Add script for generating changelog by project id and release version

User Experience
---------------
* `#2387 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2387>`_ - Investigation multiple warnings for binding in NU cluster for singularity
* `#2145 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2145>`_ - slurm platform -- unable to run from compute nodes as expected
