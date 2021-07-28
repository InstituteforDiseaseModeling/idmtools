
=====
1.0.1
=====


1.0.1 - Analyzers
-----------------
* `#0778 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/778>`_ - Add support for context platforms to analyzer manager


1.0.1 - Bugs
------------
* `#0637 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/637>`_ - pytest: ValueError: I/O operation on closed file, Printed at the end of tests.
* `#0663 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/663>`_ - SSMT PlatformAnalysis can not put 2 analyzers in same file as main entry
* `#0696 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/696>`_ - Rename num_retires to num_retries on COMPS Platform
* `#0702 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/702>`_ - Can not analyze workitem
* `#0739 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/739>`_ - Logging should load defaults with default config block is missing
* `#0741 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/741>`_ - MAX_PATH issues with RequirementsToAssetCollection WI create_asset_collection
* `#0752 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/752>`_ - type hint in analyzer_manager is wrong
* `#0758 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/758>`_ - Workitem config should be validated on WorkItem for PythonAsset Collection 
* `#0776 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/776>`_ - Fix hook execution order for pre_creation
* `#0779 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/779>`_ - Additional Sims is not being detected on TemplatedSimulations
* `#0788 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/788>`_ - Correct requirements on core
* `#0791 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/791>`_ - Missing asset file with RequirementsToAssetCollection


1.0.1 - Core
------------
* `#0343 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/343>`_ - Genericize experiment_factory to work for other items
* `#0611 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/611>`_ - Consider excluding idmtools.log and COMPS_log.log on SSMT WI submission
* `#0737 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/737>`_ - Remove standalone builder in favor of regular python


1.0.1 - Developer/Test
----------------------
* `#0083 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/83>`_ - Setup python linting for the Pull requests
* `#0671 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/671>`_ - Python Linting
* `#0735 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/735>`_ - Tag or remove local tests in idmtools-core tests
* `#0736 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/736>`_ - Mark set of smoke tests to run in github actions
* `#0773 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/773>`_ - Move model-emod to new repo
* `#0794 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/794>`_ - build idmtools_platform_local fail with idmtools_webui error


1.0.1 - Documentation
---------------------
* `#0015 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/15>`_ - Add cookiecutter projects
* `#0423 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/423>`_ - Create a clear document on what features are provided by what packages
* `#0473 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/473>`_ - Create sweep without builder
* `#0476 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/476>`_ - ARM builder
* `#0477 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/477>`_ - CSV builder
* `#0478 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/478>`_ - YAML builder
* `#0487 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/487>`_ - Creation of an analyzer
* `#0488 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/488>`_ - Base analyzer - Constructor
* `#0489 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/489>`_ - Base analyzer - Filter function
* `#0490 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/490>`_ - Base analyzer - Parsing
* `#0491 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/491>`_ - Base analyzer - Working directory
* `#0492 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/492>`_ - Base analyzer - Map function
* `#0493 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/493>`_ - Base analyzer - Reduce function
* `#0494 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/494>`_ - Base analyzer - per group function
* `#0495 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/495>`_ - Base analyzer - Destroy function
* `#0496 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/496>`_ - Features of AnalyzeManager - Overview
* `#0497 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/497>`_ - Features of AnalyzeManager - Partial analysis
* `#0498 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/498>`_ - Features of AnalyzeManager - Max items
* `#0499 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/499>`_ - Features of AnalyzeManager - Working directory forcing
* `#0500 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/500>`_ - Features of AnalyzeManager - Adding items
* `#0501 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/501>`_ - Built-in analyzers - InsetChart analyzer
* `#0502 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/502>`_ - Built-in analyzers - CSV Analyzer
* `#0503 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/503>`_ - Built-in analyzers - Tags analyzer
* `#0504 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/504>`_ - Built-in analyzers - Download analyzer
* `#0508 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/508>`_ - Logging and Debugging
* `#0509 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/509>`_ - Global parameters
* `#0511 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/511>`_ - COMPS platform options
* `#0629 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/629>`_ - Update docker endpoint on ssmt/local platform to use external endpoint for pull/running 
* `#0630 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/630>`_ - Investigate packaging idmtools as wheel file
* `#0714 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/714>`_ - Document the Versioning details
* `#0717 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/717>`_ - Sweep Simulation Builder
* `#0720 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/720>`_ - Documentation on Analyzing Failed experiments
* `#0721 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/721>`_ - AddAnalyer should have example in its self documentation
* `#0722 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/722>`_ - CSVAnalyzer should have example in its self documentation
* `#0723 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/723>`_ - DownloadAnalyzer should have example in its self documentation
* `#0724 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/724>`_ - PlatformAnalysis should have explanation of its used documented
* `#0727 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/727>`_ - SimulationBuilder Sweep builder documentation
* `#0734 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/734>`_ - idmtools does not install dataclasses on python3.6
* `#0751 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/751>`_ - Switch to apidoc generated RSTs for modules and remove from source control


1.0.1 - Feature Request
-----------------------
* `#0059 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/59>`_ - Chaining of Analyzers
* `#0097 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/97>`_ - Ability to batch simulations within simulation
* `#0704 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/704>`_ - Tthere is no way to  load custom wheel using the RequirementsToAssets utility
* `#0784 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/784>`_ - Remove default node_group value 'emod_abcd' from platform
* `#0786 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/786>`_ - Improve Suite support


1.0.1 - Platforms
-----------------
* `#0277 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/277>`_ - Need way to add tags to COMPSPlatform ACs after creation
* `#0638 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/638>`_ - Change print statement to logger in python_requirements_ac utility
* `#0640 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/640>`_ - Better error reporting when the python_requirements_ac fails
* `#0651 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/651>`_ - A user should not need to specify the default SSMT image
* `#0688 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/688>`_ - Load Custom Library Utility should support install packages from Artifactory
* `#0705 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/705>`_ - Should have way to regenerate AssetCollection id from RequirementsToAssetCollection
* `#0757 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/757>`_ - Set PYTHONPATH on Slurm


1.0.1 - User Experience
-----------------------
* `#0760 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/760>`_ - Email for issues and feature requests
* `#0781 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/781>`_ - Suites should support run on object
* `#0787 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/787>`_ - idmtools should print experiment id by default in console
