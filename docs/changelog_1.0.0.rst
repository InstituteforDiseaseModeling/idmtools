=====
1.0.0
=====


Analyzers
---------
* `#0196 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/196>`_ - Filtering
* `#0197 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/197>`_ - Select_simulation_data
* `#0198 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/198>`_ - Finalize
* `#0279 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/279>`_ - Port dtk-tools analyze system to idmtools
* `#0282 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/282>`_ - Add unit and basic end-to-end tests for AnalyzeManager class
* `#0283 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/283>`_ - Fix up all platform-based test due to analyzer/platform refactor/genericization
* `#0337 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/337>`_ - Change AnalyzeManager to support passing ids (Experiment, Simulation, Suite)
* `#0338 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/338>`_ - Two AnalyzeManager files - one incorrect and needs to be removed
* `#0340 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/340>`_ - Cleanup DownloadAnalyzer
* `#0344 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/344>`_ - AnalyzeManager configuration should be option parameter
* `#0592 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/592>`_ - analyzers error on platform.get_files for COMPS: argument of type 'NoneType' is not iterable
* `#0594 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/594>`_ - analyzer error multiprocessing pool StopIteration error in finalize_results
* `#0614 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/614>`_ - Convenience function to exclude items in analyze manager
* `#0619 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/619>`_ - Ability to get exp sim object ids in analyzers


Bugs
----
* `#0124 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/124>`_ - Can not run tests\test_python_simulation.py from console
* `#0125 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/125>`_ - relative_path for AssetCollection does not work
* `#0129 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/129>`_ - new python model root node changed from "config" to "parameters"
* `#0142 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/142>`_ - experiment.batch_simulations seems not doing batch
* `#0143 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/143>`_ - COMPSPlatform's refresh_experiment_status() get called too much from ExperimentManager's wait_till_done() mathod
* `#0150 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/150>`_ - missing pandas package
* `#0170 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/170>`_ - tag "type: idmtools_models.python.PythonExperiment" can be missing for same test
* `#0184 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/184>`_ - Missing 'data' dir for test_experiment_manager test. (TestPlatform)
* `#0223 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/223>`_ - UnicodeDecodeError for testcases in test_dtk.py when run with LocalPlatform
* `#0236 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/236>`_ - LocalRunner: ExperimentsClient get_all method should have parameter 'tags' not 'tag'
* `#0265 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/265>`_ - load_files for DTKExperiment create nested 'parameters' in config.json
* `#0266 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/266>`_ - load_files for demographics.json does not work
* `#0294 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/294>`_ - Docker containers failed to start if they are created but stopped
* `#0302 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/302>`_ - Local Platform delete is broken
* `#0304 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/304>`_ - Fix issue if failure during start of local platform the spinner continue to spin
* `#0323 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/323>`_ - idmtools is not retro-compatible with pre-idmtools experiments
* `#0332 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/332>`_ - with large number of simulations, local platform either timeout on dramatiq or stuck on persistamceService save method
* `#0339 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/339>`_ - Analyzer tests fails on AnalyzeManager analyze len(self.potential_items) == 0
* `#0341 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/341>`_ - AnalyzeManager Runtime error on worker_pool
* `#0345 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/345>`_ - PlatformFactory broken existing test in branch 'analyze-manager-port'
* `#0346 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/346>`_ - UnknownItemException for analyzers on COMPSPlatform PythonExperiments
* `#0350 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/350>`_ - RunTask in local platform should catch exception
* `#0351 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/351>`_ - AnalyzeManager finalize_results Process cannot access the cache.db because it is being used by another process
* `#0352 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/352>`_ - Current structure of code leads to circular dependencies or classes as modules
* `#0375 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/375>`_ - AnalyzerManager does not work for case to add experiment to analyzermanager
* `#0376 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/376>`_ - AnalyzerManager does not work for simulation
* `#0378 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/378>`_ - experiment/simulation display and print are messed up in latest dev
* `#0386 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/386>`_ - Local platform cannot create more than 20 simulations in a given experiment
* `#0389 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/389>`_ - Dev branch's docker repo is missing 0.2.0.nightly image which LocalPlatform needs
* `#0398 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/398>`_ - Ensure that redis and postgres ports work as expected
* `#0425 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/425>`_ - Idmtools should still support old Eradication.exe
* `#0427 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/427>`_ - Access to the experiment object in analyzers
* `#0429 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/429>`_ - Cleanup_cache fails PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
* `#0458 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/458>`_ - There is no way to add custom tags to simulations
* `#0465 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/465>`_ - BuilderExperiment for sweep "string" is wrong
* `#0560 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/560>`_ - docker-compose build does not work for r-model example
* `#0562 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/562>`_ - workflow_item_operations get workitem querycriteria fails
* `#0572 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/572>`_ - python 3.7.3 less version will fail for task type changing
* `#0585 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/585>`_ - print(platform) throws exception for Python 3.6
* `#0588 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/588>`_ - Running the dev installation in a virtualenv "installs" it globally
* `#0598 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/598>`_ - CSVAnalyzer pass wrong value to parse in super().__init__ call
* `#0602 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/602>`_ - Analyzer doesn't work for my Python SEIR model
* `#0605 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/605>`_ - When running multiple analyzers together, 'data' in one analyzer should not contains data from other analyzer
* `#0608 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/608>`_ - Can not add custom tag to AssetCollection in idmtools
* `#0616 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/616>`_ - AssetCollection pre_creation failed if no tag
* `#0641 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/641>`_ - Remove unused code in the python_requirements_ac
* `#0643 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/643>`_ - "pymake ssmt-image-local" in idmtools_platform_comps not working
* `#0644 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/644>`_ - Platform cannot run workitem directly
* `#0646 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/646>`_ - platform.get_items(ac) not return tags


CLI
---
* `#0009 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/9>`_ - Boilerplate command
* `#0118 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/118>`_ - Add the printing of children in the EntityContainer
* `#0187 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/187>`_ - Move the CLI package to idmtools/cli
* `#0188 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/188>`_ - Ensure the dependencies are moved from local_runner to idmtools
* `#0190 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/190>`_ - Add a platform attribute to the CLI commands
* `#0191 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/191>`_ - Create a PlatformFactory
* `#0241 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/241>`_ - CLI should be distinct package and implement as plugins
* `#0251 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/251>`_ - Setup for the CLI package should provide a entrypoint for easy use of commands
* `#0252 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/252>`_ - Add --debug to cli main level


Configuration
-------------
* `#0248 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/248>`_ - Logging needs to support user configuration through the idmtools.ini
* `#0392 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/392>`_ - Improve IdmConfigParser: make decorator for ensure_ini() method...
* `#0597 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/597>`_ - Platform should not be case sensitive.


Core
----
* `#0081 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/81>`_ - Allows the sweeps to be created in arms
* `#0091 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/91>`_ - Refactor the Experiment/Simulation objects to not persist the simulations
* `#0141 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/141>`_ - Standard Logging throughout tools
* `#0166 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/166>`_ - docker-compose needs to in prerequisite 
* `#0169 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/169>`_ - Handle 3.6 requirements automatically
* `#0200 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/200>`_ - Platforms should be plugins
* `#0238 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/238>`_ - Simulations of Experiment should be made pickle ignored
* `#0244 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/244>`_ - Inputs values needs to be validated when creating a Platform
* `#0257 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/257>`_ - CsvExperimentBuilder does not handle csv field with empty space
* `#0268 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/268>`_ - demographics filenames should be loaded to asset collection
* `#0281 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/281>`_ - Improve Platform to display selected Block info when creating a platform
* `#0297 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/297>`_ - Fix issues with platform factory
* `#0307 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/307>`_ - idmtools: Packages names should be consistent
* `#0315 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/315>`_ - Basic support of suite in the tools
* `#0357 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/357>`_ - ExperimentPersistService.save are not consistent
* `#0359 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/359>`_ - SimulationPersistService is not used in Idmtools
* `#0361 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/361>`_ - assets in Experiment should be made "pickle-ignore"
* `#0362 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/362>`_ - base_simulation in Experiment should be made "pickle-ignore"
* `#0368 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/368>`_ - PersistService should support clear() method
* `#0369 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/369>`_ - The method create_simulations of Experiment should consider pre-defined max_workers and batch_size in idmtools.ini
* `#0370 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/370>`_ - Add unit test for deepcopy on simulations
* `#0371 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/371>`_ - Wrong type for platform_id in IEntity definition
* `#0391 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/391>`_ - Improve Asset and AssetCollection classes by using @dataclass (field) for clear comparison
* `#0394 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/394>`_ - Remove the ExperimentPersistService
* `#0438 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/438>`_ - Support pulling Eradication from URLs and bamboo
* `#0518 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/518>`_ - Add a task class.
* `#0520 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/520>`_ - Rename current experiment builders to sweep builders
* `#0526 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/526>`_ - Create New Generic Experiment Class
* `#0527 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/527>`_ - Create new Generic Simulation Class
* `#0528 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/528>`_ - Remove old Experiments/Simulations
* `#0529 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/529>`_ - Create New Task API 
* `#0530 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/530>`_ - Rename current model api to simulation/experiment API.
* `#0538 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/538>`_ - Refactor platform interface into subinterfaces


Developer/Test
--------------
* `#0631 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/631>`_ - Ensure setup.py is consistent throughout


Documentation
-------------
* `#0100 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/100>`_ - Installation steps documented for users
* `#0312 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/312>`_ - idmtools: there is a typo in README
* `#0486 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/486>`_ - Overview of the analysis in idmtools
* `#0578 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/578>`_ - Add installation for users 
* `#0593 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/593>`_ - Simple Python SEIR model demo example 
* `#0632 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/632>`_ - Update idmtools_core setup.py to remove model emod from idm install


Feature Request
---------------
* `#0233 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/233>`_ - Add local runner timeout
* `#0437 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/437>`_ - Prompt users for docker credentials when not available
* `#0603 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/603>`_ - Implement install custom requirement libs to asset collection with WorkItem


Models
------
* `#0024 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/24>`_ - R Model support
* `#0053 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/53>`_ - Support of demographics files
* `#0212 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/212>`_ - Models should be plugins
* `#0287 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/287>`_ - Add info about support models/docker support to platform
* `#0288 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/288>`_ - Create DockerExperiment and subclasses
* `#0519 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/519>`_ - Move experiment building to ExperimentBuilder
* `#0521 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/521>`_ - Create Generic Dictionary Config Task
* `#0522 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/522>`_ - Create PythonTask
* `#0523 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/523>`_ - Create PythonDictionaryTask
* `#0524 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/524>`_ - Create RTask
* `#0525 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/525>`_ - Create EModTask
* `#0535 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/535>`_ - Create DockerTask


Platforms
---------
* `#0027 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/27>`_ - SSMT Platform
* `#0072 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/72>`_ - [Local Runner] Cancelling capabilities
* `#0094 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/94>`_ - Batch and parallelize simulation creation in the COMPSPlatform
* `#0122 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/122>`_ - Ability to create an AssetCollection based on a COMPS asset collection id
* `#0130 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/130>`_ - User configuration and data storage location
* `#0186 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/186>`_ - The `local_runner` client should move to the `idmtools` package
* `#0194 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/194>`_ - COMPS Files retrieval system
* `#0195 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/195>`_ - LOCAL Files retrieval system
* `#0221 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/221>`_ - Local runner for experiment/simulations have different file hierarchy than COMPS 
* `#0254 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/254>`_ - Local Platform Asset should be implemented via API or Docker socket
* `#0264 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/264>`_ - idmtools_local_runner's tasks/run.py should have better handle for unhandled exception
* `#0276 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/276>`_ - Docker services should be started for end-users without needing to use docker-compose
* `#0280 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/280>`_ - Generalize sim/exp/suite format of ISimulation, IExperiment, IPlatform
* `#0286 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/286>`_ - Add special GPU queue to Local Platform
* `#0306 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/306>`_ - AssetCollection's assets_from_directory logic wrong if set flatten and relative path at same time
* `#0314 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/314>`_ - Fix local platform to work with latest analyze/platform updates
* `#0316 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/316>`_ - Integrate website with Local Runner Container
* `#0329 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/329>`_ - Experiment level status
* `#0330 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/330>`_ - Paging on simulation/experiment APIs for better UI experience
* `#0333 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/333>`_ - ensure pyComps allows compatible releases 
* `#0364 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/364>`_ - Local platform should use production artfactory for docker images
* `#0381 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/381>`_ - Support Work Items in COMPS Platform
* `#0387 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/387>`_ - Local platform webUI only show simulations up to 20
* `#0393 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/393>`_ - local platform tests keep getting EOFError while logger is in DEBUG and console is on
* `#0405 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/405>`_ - Support analysis of data from Work Items in Analyze Manager
* `#0407 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/407>`_ - Support Service Side Analysis through SSMT
* `#0447 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/447>`_ - Set limitation for docker container's access to memory
* `#0532 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/532>`_ - Make updates to ExperimentManager/Platform to support tasks
* `#0540 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/540>`_ - Create initial SSMT Plaform from COMPS Platform
* `#0596 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/596>`_ - COMPSPlatform.get_files(item,..) not working for Experiment or Suite
* `#0635 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/635>`_ - Update SSMT base image
* `#0639 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/639>`_ - Add a way for the python_requirements_ac to use additional wheel file
* `#0676 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/676>`_ - ssmt missing QueryCriteria support
* `#0677 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/677>`_ - ssmt: refresh_status returns None


User Experience
---------------
* `#0457 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/457>`_ - Option to analyze failed simulations
