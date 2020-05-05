=====
1.0.0
=====


Analyzers
---------
* `#0196 https://github.com/InstituteforDiseaseModeling/idmtools/issues/196` - Filtering
* `#0197 https://github.com/InstituteforDiseaseModeling/idmtools/issues/197` - Select_simulation_data
* `#0198 https://github.com/InstituteforDiseaseModeling/idmtools/issues/198` - Finalize
* `#0279 https://github.com/InstituteforDiseaseModeling/idmtools/issues/279` - Port dtk-tools analyze system to idmtools
* `#0282 https://github.com/InstituteforDiseaseModeling/idmtools/issues/282` - Add unit and basic end-to-end tests for AnalyzeManager class
* `#0283 https://github.com/InstituteforDiseaseModeling/idmtools/issues/283` - Fix up all platform-based test due to analyzer/platform refactor/genericization
* `#0337 https://github.com/InstituteforDiseaseModeling/idmtools/issues/337` - Change AnalyzeManager to support passing ids (Experiment, Simulation, Suite)
* `#0338 https://github.com/InstituteforDiseaseModeling/idmtools/issues/338` - Two AnalyzeManager files - one incorrect and needs to be removed
* `#0340 https://github.com/InstituteforDiseaseModeling/idmtools/issues/340` - Cleanup DownloadAnalyzer
* `#0344 https://github.com/InstituteforDiseaseModeling/idmtools/issues/344` - AnalyzeManager configuration should be option parameter
* `#0592 https://github.com/InstituteforDiseaseModeling/idmtools/issues/592` - analyzers error on platform.get_files for COMPS: argument of type 'NoneType' is not iterable
* `#0594 https://github.com/InstituteforDiseaseModeling/idmtools/issues/594` - analyzer error multiprocessing pool StopIteration error in finalize_results
* `#0614 https://github.com/InstituteforDiseaseModeling/idmtools/issues/614` - Convenience function to exclude items in analyze manager
* `#0619 https://github.com/InstituteforDiseaseModeling/idmtools/issues/619` - Ability to get exp sim object ids in analyzers


Bugs
----
* `#0124 https://github.com/InstituteforDiseaseModeling/idmtools/issues/124` - Can not run tests\test_python_simulation.py from console
* `#0125 https://github.com/InstituteforDiseaseModeling/idmtools/issues/125` - relative_path for AssetCollection does not work
* `#0129 https://github.com/InstituteforDiseaseModeling/idmtools/issues/129` - new python model root node changed from "config" to "parameters"
* `#0142 https://github.com/InstituteforDiseaseModeling/idmtools/issues/142` - experiment.batch_simulations seems not doing batch
* `#0143 https://github.com/InstituteforDiseaseModeling/idmtools/issues/143` - COMPSPlatform's refresh_experiment_status() get called too much from ExperimentManager's wait_till_done() mathod
* `#0150 https://github.com/InstituteforDiseaseModeling/idmtools/issues/150` - missing pandas package
* `#0170 https://github.com/InstituteforDiseaseModeling/idmtools/issues/170` - tag "type: idmtools_models.python.PythonExperiment" can be missing for same test
* `#0184 https://github.com/InstituteforDiseaseModeling/idmtools/issues/184` - Missing 'data' dir for test_experiment_manager test. (TestPlatform)
* `#0223 https://github.com/InstituteforDiseaseModeling/idmtools/issues/223` - UnicodeDecodeError for testcases in test_dtk.py when run with LocalPlatform
* `#0236 https://github.com/InstituteforDiseaseModeling/idmtools/issues/236` - LocalRunner: ExperimentsClient get_all method should have parameter 'tags' not 'tag'
* `#0265 https://github.com/InstituteforDiseaseModeling/idmtools/issues/265` - load_files for DTKExperiment create nested 'parameters' in config.json
* `#0266 https://github.com/InstituteforDiseaseModeling/idmtools/issues/266` - load_files for demographics.json does not work
* `#0294 https://github.com/InstituteforDiseaseModeling/idmtools/issues/294` - Docker containers failed to start if they are created but stopped
* `#0302 https://github.com/InstituteforDiseaseModeling/idmtools/issues/302` - Local Platform delete is broken
* `#0304 https://github.com/InstituteforDiseaseModeling/idmtools/issues/304` - Fix issue if failure during start of local platform the spinner continue to spin
* `#0323 https://github.com/InstituteforDiseaseModeling/idmtools/issues/323` - idmtools is not retro-compatible with pre-idmtools experiments
* `#0332 https://github.com/InstituteforDiseaseModeling/idmtools/issues/332` - with large number of simulations, local platform either timeout on dramatiq or stuck on persistamceService save method
* `#0339 https://github.com/InstituteforDiseaseModeling/idmtools/issues/339` - Analyzer tests fails on AnalyzeManager analyze len(self.potential_items) == 0
* `#0341 https://github.com/InstituteforDiseaseModeling/idmtools/issues/341` - AnalyzeManager Runtime error on worker_pool
* `#0345 https://github.com/InstituteforDiseaseModeling/idmtools/issues/345` - PlatformFactory broken existing test in branch 'analyze-manager-port'
* `#0346 https://github.com/InstituteforDiseaseModeling/idmtools/issues/346` - UnknownItemException for analyzers on COMPSPlatform PythonExperiments
* `#0350 https://github.com/InstituteforDiseaseModeling/idmtools/issues/350` - RunTask in local platform should catch exception
* `#0351 https://github.com/InstituteforDiseaseModeling/idmtools/issues/351` - AnalyzeManager finalize_results Process cannot access the cache.db because it is being used by another process
* `#0352 https://github.com/InstituteforDiseaseModeling/idmtools/issues/352` - Current structure of code leads to circular dependencies or classes as modules
* `#0375 https://github.com/InstituteforDiseaseModeling/idmtools/issues/375` - AnalyzerManager does not work for case to add experiment to analyzermanager
* `#0376 https://github.com/InstituteforDiseaseModeling/idmtools/issues/376` - AnalyzerManager does not work for simulation
* `#0378 https://github.com/InstituteforDiseaseModeling/idmtools/issues/378` - experiment/simulation display and print are messed up in latest dev
* `#0386 https://github.com/InstituteforDiseaseModeling/idmtools/issues/386` - Local platform cannot create more than 20 simulations in a given experiment
* `#0389 https://github.com/InstituteforDiseaseModeling/idmtools/issues/389` - Dev branch's docker repo is missing 0.2.0.nightly image which LocalPlatform needs
* `#0398 https://github.com/InstituteforDiseaseModeling/idmtools/issues/398` - Ensure that redis and postgres ports work as expected
* `#0425 https://github.com/InstituteforDiseaseModeling/idmtools/issues/425` - Idmtools should still support old Eradication.exe
* `#0427 https://github.com/InstituteforDiseaseModeling/idmtools/issues/427` - Access to the experiment object in analyzers
* `#0429 https://github.com/InstituteforDiseaseModeling/idmtools/issues/429` - Cleanup_cache fails PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
* `#0458 https://github.com/InstituteforDiseaseModeling/idmtools/issues/458` - There is no way to add custom tags to simulations
* `#0465 https://github.com/InstituteforDiseaseModeling/idmtools/issues/465` - BuilderExperiment for sweep "string" is wrong
* `#0560 https://github.com/InstituteforDiseaseModeling/idmtools/issues/560` - docker-compose build does not work for r-model example
* `#0562 https://github.com/InstituteforDiseaseModeling/idmtools/issues/562` - workflow_item_operations get workitem querycriteria fails
* `#0572 https://github.com/InstituteforDiseaseModeling/idmtools/issues/572` - python 3.7.3 less version will fail for task type changing
* `#0585 https://github.com/InstituteforDiseaseModeling/idmtools/issues/585` - print(platform) throws exception for Python 3.6
* `#0588 https://github.com/InstituteforDiseaseModeling/idmtools/issues/588` - Running the dev installation in a virtualenv "installs" it globally
* `#0598 https://github.com/InstituteforDiseaseModeling/idmtools/issues/598` - CSVAnalyzer pass wrong value to parse in super().__init__ call
* `#0602 https://github.com/InstituteforDiseaseModeling/idmtools/issues/602` - Analyzer doesn't work for my Python SEIR model
* `#0605 https://github.com/InstituteforDiseaseModeling/idmtools/issues/605` - When running multiple analyzers together, 'data' in one analyzer should not contains data from other analyzer
* `#0608 https://github.com/InstituteforDiseaseModeling/idmtools/issues/608` - Can not add custom tag to AssetCollection in idmtools
* `#0616 https://github.com/InstituteforDiseaseModeling/idmtools/issues/616` - AssetCollection pre_creation failed if no tag
* `#0641 https://github.com/InstituteforDiseaseModeling/idmtools/issues/641` - Remove unused code in the python_requirements_ac
* `#0643 https://github.com/InstituteforDiseaseModeling/idmtools/issues/643` - "pymake ssmt-image-local" in idmtools_platform_comps not working
* `#0644 https://github.com/InstituteforDiseaseModeling/idmtools/issues/644` - Platform cannot run workitem directly
* `#0646 https://github.com/InstituteforDiseaseModeling/idmtools/issues/646` - platform.get_items(ac) not return tags


CLI
---
* `#0009 https://github.com/InstituteforDiseaseModeling/idmtools/issues/9` - Boilerplate command
* `#0118 https://github.com/InstituteforDiseaseModeling/idmtools/issues/118` - Add the printing of children in the EntityContainer
* `#0187 https://github.com/InstituteforDiseaseModeling/idmtools/issues/187` - Move the CLI package to idmtools/cli
* `#0188 https://github.com/InstituteforDiseaseModeling/idmtools/issues/188` - Ensure the dependencies are moved from local_runner to idmtools
* `#0190 https://github.com/InstituteforDiseaseModeling/idmtools/issues/190` - Add a platform attribute to the CLI commands
* `#0191 https://github.com/InstituteforDiseaseModeling/idmtools/issues/191` - Create a PlatformFactory
* `#0241 https://github.com/InstituteforDiseaseModeling/idmtools/issues/241` - CLI should be distinct package and implement as plugins
* `#0251 https://github.com/InstituteforDiseaseModeling/idmtools/issues/251` - Setup for the CLI package should provide a entrypoint for easy use of commands
* `#0252 https://github.com/InstituteforDiseaseModeling/idmtools/issues/252` - Add --debug to cli main level


Configuration
-------------
* `#0248 https://github.com/InstituteforDiseaseModeling/idmtools/issues/248` - Logging needs to support user configuration through the idmtools.ini
* `#0392 https://github.com/InstituteforDiseaseModeling/idmtools/issues/392` - Improve IdmConfigParser: make decorator for ensure_ini() method...
* `#0597 https://github.com/InstituteforDiseaseModeling/idmtools/issues/597` - Platform should not be case sensitive.


Core
----
* `#0081 https://github.com/InstituteforDiseaseModeling/idmtools/issues/81` - Allows the sweeps to be created in arms
* `#0091 https://github.com/InstituteforDiseaseModeling/idmtools/issues/91` - Refactor the Experiment/Simulation objects to not persist the simulations
* `#0141 https://github.com/InstituteforDiseaseModeling/idmtools/issues/141` - Standard Logging throughout tools
* `#0166 https://github.com/InstituteforDiseaseModeling/idmtools/issues/166` - docker-compose needs to in prerequisite 
* `#0169 https://github.com/InstituteforDiseaseModeling/idmtools/issues/169` - Handle 3.6 requirements automatically
* `#0200 https://github.com/InstituteforDiseaseModeling/idmtools/issues/200` - Platforms should be plugins
* `#0238 https://github.com/InstituteforDiseaseModeling/idmtools/issues/238` - Simulations of Experiment should be made pickle ignored
* `#0244 https://github.com/InstituteforDiseaseModeling/idmtools/issues/244` - Inputs values needs to be validated when creating a Platform
* `#0257 https://github.com/InstituteforDiseaseModeling/idmtools/issues/257` - CsvExperimentBuilder does not handle csv field with empty space
* `#0268 https://github.com/InstituteforDiseaseModeling/idmtools/issues/268` - demographics filenames should be loaded to asset collection
* `#0281 https://github.com/InstituteforDiseaseModeling/idmtools/issues/281` - Improve Platform to display selected Block info when creating a platform
* `#0297 https://github.com/InstituteforDiseaseModeling/idmtools/issues/297` - Fix issues with platform factory
* `#0307 https://github.com/InstituteforDiseaseModeling/idmtools/issues/307` - idmtools: Packages names should be consistent
* `#0315 https://github.com/InstituteforDiseaseModeling/idmtools/issues/315` - Basic support of suite in the tools
* `#0357 https://github.com/InstituteforDiseaseModeling/idmtools/issues/357` - ExperimentPersistService.save are not consistent
* `#0359 https://github.com/InstituteforDiseaseModeling/idmtools/issues/359` - SimulationPersistService is not used in Idmtools
* `#0361 https://github.com/InstituteforDiseaseModeling/idmtools/issues/361` - assets in Experiment should be made "pickle-ignore"
* `#0362 https://github.com/InstituteforDiseaseModeling/idmtools/issues/362` - base_simulation in Experiment should be made "pickle-ignore"
* `#0368 https://github.com/InstituteforDiseaseModeling/idmtools/issues/368` - PersistService should support clear() method
* `#0369 https://github.com/InstituteforDiseaseModeling/idmtools/issues/369` - The method create_simulations of Experiment should consider pre-defined max_workers and batch_size in idmtools.ini
* `#0370 https://github.com/InstituteforDiseaseModeling/idmtools/issues/370` - Add unit test for deepcopy on simulations
* `#0371 https://github.com/InstituteforDiseaseModeling/idmtools/issues/371` - Wrong type for platform_id in IEntity definition
* `#0391 https://github.com/InstituteforDiseaseModeling/idmtools/issues/391` - Improve Asset and AssetCollection classes by using @dataclass (field) for clear comparison
* `#0394 https://github.com/InstituteforDiseaseModeling/idmtools/issues/394` - Remove the ExperimentPersistService
* `#0438 https://github.com/InstituteforDiseaseModeling/idmtools/issues/438` - Support pulling Eradication from URLs and bamboo
* `#0518 https://github.com/InstituteforDiseaseModeling/idmtools/issues/518` - Add a task class.
* `#0520 https://github.com/InstituteforDiseaseModeling/idmtools/issues/520` - Rename current experiment builders to sweep builders
* `#0526 https://github.com/InstituteforDiseaseModeling/idmtools/issues/526` - Create New Generic Experiment Class
* `#0527 https://github.com/InstituteforDiseaseModeling/idmtools/issues/527` - Create new Generic Simulation Class
* `#0528 https://github.com/InstituteforDiseaseModeling/idmtools/issues/528` - Remove old Experiments/Simulations
* `#0529 https://github.com/InstituteforDiseaseModeling/idmtools/issues/529` - Create New Task API 
* `#0530 https://github.com/InstituteforDiseaseModeling/idmtools/issues/530` - Rename current model api to simulation/experiment API.
* `#0538 https://github.com/InstituteforDiseaseModeling/idmtools/issues/538` - Refactor platform interface into subinterfaces


Developer/Test
--------------
* `#0631 https://github.com/InstituteforDiseaseModeling/idmtools/issues/631` - Ensure setup.py is consistent throughout


Documentation
-------------
* `#0100 https://github.com/InstituteforDiseaseModeling/idmtools/issues/100` - Installation steps documented for users
* `#0312 https://github.com/InstituteforDiseaseModeling/idmtools/issues/312` - idmtools: there is a typo in README
* `#0486 https://github.com/InstituteforDiseaseModeling/idmtools/issues/486` - Overview of the analysis in idmtools
* `#0578 https://github.com/InstituteforDiseaseModeling/idmtools/issues/578` - Add installation for users 
* `#0593 https://github.com/InstituteforDiseaseModeling/idmtools/issues/593` - Simple Python SEIR model demo example 
* `#0632 https://github.com/InstituteforDiseaseModeling/idmtools/issues/632` - Update idmtools_core setup.py to remove model emod from idm install


Feature Request
---------------
* `#0233 https://github.com/InstituteforDiseaseModeling/idmtools/issues/233` - Add local runner timeout
* `#0437 https://github.com/InstituteforDiseaseModeling/idmtools/issues/437` - Prompt users for docker credentials when not available
* `#0603 https://github.com/InstituteforDiseaseModeling/idmtools/issues/603` - Implement install custom requirement libs to asset collection with WorkItem


Models
------
* `#0024 https://github.com/InstituteforDiseaseModeling/idmtools/issues/24` - R Model support
* `#0053 https://github.com/InstituteforDiseaseModeling/idmtools/issues/53` - Support of demographics files
* `#0212 https://github.com/InstituteforDiseaseModeling/idmtools/issues/212` - Models should be plugins
* `#0287 https://github.com/InstituteforDiseaseModeling/idmtools/issues/287` - Add info about support models/docker support to platform
* `#0288 https://github.com/InstituteforDiseaseModeling/idmtools/issues/288` - Create DockerExperiment and subclasses
* `#0519 https://github.com/InstituteforDiseaseModeling/idmtools/issues/519` - Move experiment building to ExperimentBuilder
* `#0521 https://github.com/InstituteforDiseaseModeling/idmtools/issues/521` - Create Generic Dictionary Config Task
* `#0522 https://github.com/InstituteforDiseaseModeling/idmtools/issues/522` - Create PythonTask
* `#0523 https://github.com/InstituteforDiseaseModeling/idmtools/issues/523` - Create PythonDictionaryTask
* `#0524 https://github.com/InstituteforDiseaseModeling/idmtools/issues/524` - Create RTask
* `#0525 https://github.com/InstituteforDiseaseModeling/idmtools/issues/525` - Create EModTask
* `#0535 https://github.com/InstituteforDiseaseModeling/idmtools/issues/535` - Create DockerTask


Platforms
---------
* `#0027 https://github.com/InstituteforDiseaseModeling/idmtools/issues/27` - SSMT Platform
* `#0072 https://github.com/InstituteforDiseaseModeling/idmtools/issues/72` - [Local Runner] Cancelling capabilities
* `#0094 https://github.com/InstituteforDiseaseModeling/idmtools/issues/94` - Batch and parallelize simulation creation in the COMPSPlatform
* `#0122 https://github.com/InstituteforDiseaseModeling/idmtools/issues/122` - Ability to create an AssetCollection based on a COMPS asset collection id
* `#0130 https://github.com/InstituteforDiseaseModeling/idmtools/issues/130` - User configuration and data storage location
* `#0186 https://github.com/InstituteforDiseaseModeling/idmtools/issues/186` - The `local_runner` client should move to the `idmtools` package
* `#0194 https://github.com/InstituteforDiseaseModeling/idmtools/issues/194` - COMPS Files retrieval system
* `#0195 https://github.com/InstituteforDiseaseModeling/idmtools/issues/195` - LOCAL Files retrieval system
* `#0221 https://github.com/InstituteforDiseaseModeling/idmtools/issues/221` - Local runner for experiment/simulations have different file hierarchy than COMPS 
* `#0254 https://github.com/InstituteforDiseaseModeling/idmtools/issues/254` - Local Platform Asset should be implemented via API or Docker socket
* `#0264 https://github.com/InstituteforDiseaseModeling/idmtools/issues/264` - idmtools_local_runner's tasks/run.py should have better handle for unhandled exception
* `#0276 https://github.com/InstituteforDiseaseModeling/idmtools/issues/276` - Docker services should be started for end-users without needing to use docker-compose
* `#0280 https://github.com/InstituteforDiseaseModeling/idmtools/issues/280` - Generalize sim/exp/suite format of ISimulation, IExperiment, IPlatform
* `#0286 https://github.com/InstituteforDiseaseModeling/idmtools/issues/286` - Add special GPU queue to Local Platform
* `#0306 https://github.com/InstituteforDiseaseModeling/idmtools/issues/306` - AssetCollection's assets_from_directory logic wrong if set flatten and relative path at same time
* `#0314 https://github.com/InstituteforDiseaseModeling/idmtools/issues/314` - Fix local platform to work with latest analyze/platform updates
* `#0316 https://github.com/InstituteforDiseaseModeling/idmtools/issues/316` - Integrate website with Local Runner Container
* `#0329 https://github.com/InstituteforDiseaseModeling/idmtools/issues/329` - Experiment level status
* `#0330 https://github.com/InstituteforDiseaseModeling/idmtools/issues/330` - Paging on simulation/experiment APIs for better UI experience
* `#0333 https://github.com/InstituteforDiseaseModeling/idmtools/issues/333` - ensure pyComps allows compatible releases 
* `#0364 https://github.com/InstituteforDiseaseModeling/idmtools/issues/364` - Local platform should use production artfactory for docker images
* `#0381 https://github.com/InstituteforDiseaseModeling/idmtools/issues/381` - Support Work Items in COMPS Platform
* `#0387 https://github.com/InstituteforDiseaseModeling/idmtools/issues/387` - Local platform webUI only show simulations up to 20
* `#0393 https://github.com/InstituteforDiseaseModeling/idmtools/issues/393` - local platform tests keep getting EOFError while logger is in DEBUG and console is on
* `#0405 https://github.com/InstituteforDiseaseModeling/idmtools/issues/405` - Support analysis of data from Work Items in Analyze Manager
* `#0407 https://github.com/InstituteforDiseaseModeling/idmtools/issues/407` - Support Service Side Analysis through SSMT
* `#0447 https://github.com/InstituteforDiseaseModeling/idmtools/issues/447` - Set limitation for docker container's access to memory
* `#0532 https://github.com/InstituteforDiseaseModeling/idmtools/issues/532` - Make updates to ExperimentManager/Platform to support tasks
* `#0540 https://github.com/InstituteforDiseaseModeling/idmtools/issues/540` - Create initial SSMT Plaform from COMPS Platform
* `#0596 https://github.com/InstituteforDiseaseModeling/idmtools/issues/596` - COMPSPlatform.get_files(item,..) not working for Experiment or Suite
* `#0635 https://github.com/InstituteforDiseaseModeling/idmtools/issues/635` - Update SSMT base image
* `#0639 https://github.com/InstituteforDiseaseModeling/idmtools/issues/639` - Add a way for the python_requirements_ac to use additional wheel file
* `#0676 https://github.com/InstituteforDiseaseModeling/idmtools/issues/676` - ssmt missing QueryCriteria support
* `#0677 https://github.com/InstituteforDiseaseModeling/idmtools/issues/677` - ssmt: refresh_status returns None


User Experience
---------------
* `#0457 https://github.com/InstituteforDiseaseModeling/idmtools/issues/457` - Option to analyze failed simulations
