=====
1.6.2
=====


1.6.2 - Bugs
------------
* `#1343 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1343>`_ - Singularity Build CLI should write AssetCollection ID to file
* `#1345 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1345>`_ - Loading a platform within a Snakefile throws an exception
* `#1348 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1348>`_ - We should be able to download files using glob patterns from comps from the CLI
* `#1351 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1351>`_ - Add support to detect if target platform is windows or linux on COMPS taking into account if it is an SSMT job
* `#1363 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1363>`_ - Ensure the lookup for latest version uses only pypi not artifactory api
* `#1368 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1368>`_ - idmtools log rotation can crash in multi process environments

1.6.2 - Developer/Test
----------------------
* `#1367 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1367>`_ - Support installing SSMT packages dynamically on workitems

1.6.2 - Feature Request
-----------------------
* `#1344 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1344>`_ - Singularity Build CLI command should support writing workitem to file
* `#1349 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1349>`_ - Add support PathLike for add_asset in Assets
* `#1350 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1350>`_ - Setup global exception handler
* `#1353 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1353>`_ - Add "Assets" directory to the PYTHONPATH by default on idmtools SSMT image
* `#1366 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1366>`_ - Support adding git commit, branch, and url to Experiments, Simulations, Workitems, or other taggable entities as tags


1.6.2 - Platforms
-----------------
* `#0990 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/990>`_ - Support creating and retrieving container images in AssetCollections
* `#1352 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1352>`_ - Redirect calls to task.command to wrapped command in TemplatedScriptTask
* `#1354 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1354>`_ - AssetizeOutputs CLI should support writing to id files
