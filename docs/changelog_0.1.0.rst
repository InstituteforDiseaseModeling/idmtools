=====
0.1.0
=====


Analyzers
---------
* `#0060 https://github.com/InstituteforDiseaseModeling/idmtools/issues/60` - Analyzer base class


Bugs
----
* `#0095 https://github.com/InstituteforDiseaseModeling/idmtools/issues/95` - idmtools is not working for python 3.6
* `#0096 https://github.com/InstituteforDiseaseModeling/idmtools/issues/96` - pytest (and pytest-runner) should be installed by setup 
* `#0105 https://github.com/InstituteforDiseaseModeling/idmtools/issues/105` - UnicodeDecodeError when run python example in LocalPlatform mode
* `#0114 https://github.com/InstituteforDiseaseModeling/idmtools/issues/114` - It should be possible to set `base_simulation` in the `PythonExperiment` constructor
* `#0115 https://github.com/InstituteforDiseaseModeling/idmtools/issues/115` - `PythonSimulation` constructor should abstract the `parameters` dict
* `#0124 https://github.com/InstituteforDiseaseModeling/idmtools/issues/124` - Can not run tests\test_python_simulation.py from console
* `#0125 https://github.com/InstituteforDiseaseModeling/idmtools/issues/125` - relative_path for AssetCollection does not work
* `#0129 https://github.com/InstituteforDiseaseModeling/idmtools/issues/129` - new python model root node changed from "config" to "parameters"
* `#0137 https://github.com/InstituteforDiseaseModeling/idmtools/issues/137` - PythonExperiment fails if pass assets 
* `#0138 https://github.com/InstituteforDiseaseModeling/idmtools/issues/138` - test_sir.py does not set parameter
* `#0142 https://github.com/InstituteforDiseaseModeling/idmtools/issues/142` - experiment.batch_simulations seems not doing batch
* `#0143 https://github.com/InstituteforDiseaseModeling/idmtools/issues/143` - COMPSPlatform's refresh_experiment_status() get called too much from ExperimentManager's wait_till_done() mathod
* `#0151 https://github.com/InstituteforDiseaseModeling/idmtools/issues/151` - log throw error from IPersistanceService.py's save method
* `#0161 https://github.com/InstituteforDiseaseModeling/idmtools/issues/161` - tests/test_python_simulation.py's test_add_dirs_to_assets_comps() return different asset files for windows and linux
* `#0171 https://github.com/InstituteforDiseaseModeling/idmtools/issues/171` - Workflow: fix loop detection
* `#0203 https://github.com/InstituteforDiseaseModeling/idmtools/issues/203` - Running new builds on Linux fails in Bamboo due to data\postgres-data file folder permissions
* `#0206 https://github.com/InstituteforDiseaseModeling/idmtools/issues/206` - test_python_simulation.py failed for all local test in windows


Configuration
-------------
* `#0046 https://github.com/InstituteforDiseaseModeling/idmtools/issues/46` - Define a file format for the configuration file
* `#0047 https://github.com/InstituteforDiseaseModeling/idmtools/issues/47` - Configuration file read on a per-folder basis
* `#0048 https://github.com/InstituteforDiseaseModeling/idmtools/issues/48` - Validation for the configuration file
* `#0049 https://github.com/InstituteforDiseaseModeling/idmtools/issues/49` - Configuration file is setting correct parameters in platform
* `#0050 https://github.com/InstituteforDiseaseModeling/idmtools/issues/50` - System Configuration


Core
----
* `#0007 https://github.com/InstituteforDiseaseModeling/idmtools/issues/7` - Command line functions definition
* `#0014 https://github.com/InstituteforDiseaseModeling/idmtools/issues/14` - Package organization and pre-requisites
* `#0081 https://github.com/InstituteforDiseaseModeling/idmtools/issues/81` - Allows the sweeps to be created in arms
* `#0084 https://github.com/InstituteforDiseaseModeling/idmtools/issues/84` - Explore different backend for object storage
* `#0087 https://github.com/InstituteforDiseaseModeling/idmtools/issues/87` - Raise an exception if we have 2 files with the same relative path in the asset collection
* `#0091 https://github.com/InstituteforDiseaseModeling/idmtools/issues/91` - Refactor the Experiment/Simulation objects to not persist the simulations
* `#0092 https://github.com/InstituteforDiseaseModeling/idmtools/issues/92` - Generalize the simulations/experiments for Experiment/Suite
* `#0102 https://github.com/InstituteforDiseaseModeling/idmtools/issues/102` - [Local Runner] Retrieve simulations for experiment
* `#0107 https://github.com/InstituteforDiseaseModeling/idmtools/issues/107` - LocalPlatform does not detect duplicate files in AssetCollectionFile for pythonExperiment
* `#0118 https://github.com/InstituteforDiseaseModeling/idmtools/issues/118` - Add the printing of children in the EntityContainer
* `#0140 https://github.com/InstituteforDiseaseModeling/idmtools/issues/140` - Fetch simulations at runtime
* `#0148 https://github.com/InstituteforDiseaseModeling/idmtools/issues/148` - Add python tasks
* `#0149 https://github.com/InstituteforDiseaseModeling/idmtools/issues/149` - Create a basic iterative workflow example
* `#0150 https://github.com/InstituteforDiseaseModeling/idmtools/issues/150` - missing pandas package
* `#0180 https://github.com/InstituteforDiseaseModeling/idmtools/issues/180` - switch prettytable for tabulate


Developer/Test
--------------
* `#0088 https://github.com/InstituteforDiseaseModeling/idmtools/issues/88` - Test the install procedure
* `#0089 https://github.com/InstituteforDiseaseModeling/idmtools/issues/89` - Explore the examples and base classes
* `#0103 https://github.com/InstituteforDiseaseModeling/idmtools/issues/103` - Create a TestPlatform 
* `#0104 https://github.com/InstituteforDiseaseModeling/idmtools/issues/104` - Test the fetching of children objects at runtime. 
* `#0117 https://github.com/InstituteforDiseaseModeling/idmtools/issues/117` - Create an environment variable to run the COMPS related tests or not


Documentation
-------------
* `#0085 https://github.com/InstituteforDiseaseModeling/idmtools/issues/85` - Setup Sphinx and GitHub pages for the docs
* `#0090 https://github.com/InstituteforDiseaseModeling/idmtools/issues/90` - "Development installation steps" missing some steps


Models
------
* `#0113 https://github.com/InstituteforDiseaseModeling/idmtools/issues/113` - Create a draft DTKConfigBuilder equivalent 
* `#0136 https://github.com/InstituteforDiseaseModeling/idmtools/issues/136` - Create an envelope argument for the PythonSimulation 


Platforms
---------
* `#0068 https://github.com/InstituteforDiseaseModeling/idmtools/issues/68` - [Local Runner] Simulation status monitoring
* `#0069 https://github.com/InstituteforDiseaseModeling/idmtools/issues/69` - [Local Runner] Database
* `#0094 https://github.com/InstituteforDiseaseModeling/idmtools/issues/94` - Batch and parallelize simulation creation in the COMPSPlatform
