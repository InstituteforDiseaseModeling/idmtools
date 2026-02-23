.. _changelog-2.2.0:


=====
2.2.0
=====

Bugs
----
* `#2478 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2478>`_ - bootstrap.py didn't initialize logging well
* `#2207 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2207>`_ - Fix AnalyzeManager: output message
* `#2502 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2502>`_ - AnalyzeManager not able to retrieve assets files
* `#2503 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2503>`_ - get_files failed with COMPS Simulation

Core
----
* `#2469 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2469>`_ - Remove sequence id utility
* `#2473 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2473>`_ - Update plugin and alias

Developer/Test
--------------
* `#2472 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2472>`_ - Test calibration with new changes
* `#2474 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2474>`_ - Update dev scripts
* `#2476 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2476>`_ - Update unit tests 
* `#2484 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2484>`_ - Remove slurm utils GA related scripts
* `#2490 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2490>`_ - Test AnalyzeManager and PlatformAnalysis

Documentation
-------------
* `#2475 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2475>`_ - Update idmtools documents
* `#2535 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2535>`_ - Intermittent Sphinx Build Failures Triggered by PUML Rendering

Feature Request
---------------
* `#2493 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2493>`_ - Epic: Add tag-based filtering and other utility enhancements
* `#2494 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2494>`_ - Reallocate JobHistory utility and we may use it in other platforms
* `#2498 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2498>`_ - Add get_directory methods for Suite\Experiment\Simulations
* `#2499 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2499>`_ - Add get_simulations() and get_experiments()
* `#2500 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2500>`_ - Add simulation filtering with tags
* `#2504 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2504>`_ - get_files is case-sensitive on files names
* `#2510 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2510>`_ - Reduce UI tags space used by idmtools task_type tag in Simulation/Experiment

Other
-----
* `#2477 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2477>`_ - Refactor Slurm Platform: prepare new idmtools 2.2.0 release
* `#2491 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2491>`_ - Work with EMOD team to test before the release

Platforms
---------
* `#2424 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2424>`_ - Epic: Refactor SLURMPlatform to reduce the duplicate coding
* `#2465 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2465>`_ - Update tests and GHA for SLURM platform change
* `#2466 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2466>`_ - Make SlurmPlatform inherit from FilePlatform
* `#2467 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2467>`_ - Refactor FilePlatform
* `#2468 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2468>`_ - Remove bridged and remote utility
* `#2483 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2483>`_ - Remove mode related functions
* `#2488 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2488>`_ - Consolidate FileExperiment, SlurmExperiment, etc.
* `#2489 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2489>`_ - Refactor flatten_item method

Support
-------
* `#2482 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2482>`_ - bootstrap.py may encounter "Access is denied." issue
