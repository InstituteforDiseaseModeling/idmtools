=====
1.0.1
=====


Analyzers
---------
* `#0778 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/778>`_ - Add support for context platforms to analyzer manager


Bugs
----
* `#0643 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/643>`_ - "pymake ssmt-image-local" in idmtools_platform_comps not working
* `#0663 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/663>`_ - SSMT PlatformAnalysis can not put 2 analyzers in same file as main entry
* `#0696 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/696>`_ - Rename num_retires to num_retries on COMPS Platform
* `#0702 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/702>`_ - Can not analyze workitem
* `#0739 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/739>`_ - Make it where you can run without a logging block
* `#0741 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/741>`_ - MAX_PATH issues with RequirementsToAssetCollection WI create_asset_collection
* `#0750 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/750>`_ - Error in documentation builds around idmtoolds_dockertask
* `#0758 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/758>`_ - Workitem config should be validated on WorkItem for PythonAsset Collection 
* `#0776 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/776>`_ - Fix hook execution order for pre_creation
* `#0779 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/779>`_ - Additional Sims is not being detected on TemplatedSimulations
* `#0780 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/780>`_ - Typo in the README.md
* `#0788 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/788>`_ - Correct requirements on core
* `#0791 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/791>`_ - Missing asset file with RequirementsToAssetCollection


Core
----
* `#0611 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/611>`_ - Consider excluding idmtools.log and COMPS_log.log on SSMT WI submission
* `#0737 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/737>`_ - Remove standalone builder in favor of regular python


Developer/Test
--------------
* `#0083 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/83>`_ - Setup python linting for the Pull requests
* `#0773 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/773>`_ - Move model-emod to new repo
* `#0794 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/794>`_ - build idmtools_platform_local fail with idmtools_webui error


Documentation
-------------
* `#0423 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/423>`_ - Create a clear document on what features are provided by what packages
* `#0476 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/476>`_ - ARM builder
* `#0477 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/477>`_ - CSV builder
* `#0478 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/478>`_ - YAML builder
* `#0499 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/499>`_ - Features of AnalyzeManager - Working directory forcing
* `#0508 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/508>`_ - Logging and Debugging
* `#0509 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/509>`_ - Global parameters
* `#0630 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/630>`_ - Investigate packaging idmtools as wheel file
* `#0714 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/714>`_ - Document the Versioning details
* `#0717 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/717>`_ - Sweep Simulation Builder
* `#0720 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/720>`_ - Documentation on Analyzing Failed experiments
* `#0721 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/721>`_ - AddAnalyer should have example in its self documentation
* `#0722 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/722>`_ - CSVAnalyzer should have example in its self documentation
* `#0723 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/723>`_ - DownloadAnalyzer should have example in its self documentation
* `#0724 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/724>`_ - PlatformAnalysis should have explanation of its used documented
* `#0727 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/727>`_ - SimulationBuilder Sweep builder documentation
* `#0732 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/732>`_ - Move idmtools docs out of out Documentation Repo
* `#0734 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/734>`_ - idmtools does not install dataclasses on python3.6
* `#0751 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/751>`_ - Switch to apidoc generated RSTs for modules and remove from source control


Feature Request
---------------
* `#0704 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/704>`_ - there is no way to just load custom wheel
* `#0784 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/784>`_ - Remove default node_group value 'emod_abcd' from platform
* `#0786 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/786>`_ - Improve Suite support


Platforms
---------
* `#0277 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/277>`_ - Need way to add tags to COMPSPlatform ACs after creation
* `#0638 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/638>`_ - Change print statement to logger in python_requirements_ac utility
* `#0640 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/640>`_ - Better error reporting when the python_requirements_ac fails
* `#0651 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/651>`_ - A user should not need to specify the default SSMT image
* `#0688 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/688>`_ - Load Custom Library Utility should support install packages from Artifactory
* `#0705 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/705>`_ - Should have way to regenerate AssetCollection id from RequirementsToAssetCollection
* `#0757 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/757>`_ - Set PYTHONPATH on Slurm


User Experience
---------------
* `#0760 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/760>`_ - Email for issues and feature requests
* `#0781 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/781>`_ - Suites should support run on object
* `#0787 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/787>`_ - idmtools should print experiment id by default in console
