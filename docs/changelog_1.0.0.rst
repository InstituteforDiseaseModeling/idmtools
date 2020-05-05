=====
1.0.0
=====


Analyzers
---------
* [#0196](https://github.com/InstituteforDiseaseModeling/idmtools/issues/196) - Filtering by ckirkman-IDM
* [#0197](https://github.com/InstituteforDiseaseModeling/idmtools/issues/197) - Select_simulation_data by ckirkman-IDM
* [#0198](https://github.com/InstituteforDiseaseModeling/idmtools/issues/198) - Finalize by ckirkman-IDM
* [#0279](https://github.com/InstituteforDiseaseModeling/idmtools/issues/279) - Port dtk-tools analyze system to idmtools by ckirkman-IDM
* [#0282](https://github.com/InstituteforDiseaseModeling/idmtools/issues/282) - Add unit and basic end-to-end tests for AnalyzeManager class by ckirkman-IDM
* [#0283](https://github.com/InstituteforDiseaseModeling/idmtools/issues/283) - Fix up all platform-based test due to analyzer/platform refactor/genericization by ckirkman-IDM
* [#0314](https://github.com/InstituteforDiseaseModeling/idmtools/issues/314) - Fix local platform to work with latest analyze/platform updates by ckirkman-IDM
* [#0337](https://github.com/InstituteforDiseaseModeling/idmtools/issues/337) - Change AnalyzeManager to support passing ids (Experiment, Simulation, Suite) by ckirkman-IDM
* [#0338](https://github.com/InstituteforDiseaseModeling/idmtools/issues/338) - Two AnalyzeManager files - one incorrect and needs to be removed by ckirkman-IDM
* [#0340](https://github.com/InstituteforDiseaseModeling/idmtools/issues/340) - Cleanup DownloadAnalyzer by ckirkman-IDM
* [#0344](https://github.com/InstituteforDiseaseModeling/idmtools/issues/344) - AnalyzeManager configuration should be option parameter by ckirkman-IDM
* [#0592](https://github.com/InstituteforDiseaseModeling/idmtools/issues/592) - analyzers error on platform.get_files for COMPS: argument of type 'NoneType' is not iterable by ZDu-IDM
* [#0594](https://github.com/InstituteforDiseaseModeling/idmtools/issues/594) - analyzer error multiprocessing pool StopIteration error in finalize_results by mfisher-idmod
* [#0614](https://github.com/InstituteforDiseaseModeling/idmtools/issues/614) - Convenience function to exclude items in analyze manager by Clark Kirkman IV
* [#0619](https://github.com/InstituteforDiseaseModeling/idmtools/issues/619) - Ability to get exp sim object ids in analyzers by Clark Kirkman IV


Bugs
----
* [#0124](https://github.com/InstituteforDiseaseModeling/idmtools/issues/124) - Can not run tests\test_python_simulation.py from console by Benoit Raybaud
* [#0125](https://github.com/InstituteforDiseaseModeling/idmtools/issues/125) - relative_path for AssetCollection does not work by Benoit Raybaud
* [#0129](https://github.com/InstituteforDiseaseModeling/idmtools/issues/129) - new python model root node changed from "config" to "parameters" by Benoit Raybaud
* [#0142](https://github.com/InstituteforDiseaseModeling/idmtools/issues/142) - experiment.batch_simulations seems not doing batch by Benoit Raybaud
* [#0143](https://github.com/InstituteforDiseaseModeling/idmtools/issues/143) - COMPSPlatform's refresh_experiment_status() get called too much from ExperimentManager's wait_till_done() mathod by Benoit Raybaud
* [#0170](https://github.com/InstituteforDiseaseModeling/idmtools/issues/170) - tag "type: idmtools_models.python.PythonExperiment" can be missing for same test by Benoit Raybaud
* [#0184](https://github.com/InstituteforDiseaseModeling/idmtools/issues/184) - Missing 'data' dir for test_experiment_manager test. (TestPlatform) by zdu
* [#0223](https://github.com/InstituteforDiseaseModeling/idmtools/issues/223) - UnicodeDecodeError for testcases in test_dtk.py when run with LocalPlatform by Clinton Collins
* [#0228](https://github.com/InstituteforDiseaseModeling/idmtools/issues/228) - Fix-194 is still not working for python 3.6 in Linux by Benoit Raybaud
* [#0236](https://github.com/InstituteforDiseaseModeling/idmtools/issues/236) - LocalRunner: ExperimentsClient get_all method should have parameter 'tags' not 'tag' by Sharon Chen
* [#0265](https://github.com/InstituteforDiseaseModeling/idmtools/issues/265) - load_files for DTKExperiment create nested 'parameters' in config.json by ZDu-IDM
* [#0266](https://github.com/InstituteforDiseaseModeling/idmtools/issues/266) - load_files for demographics.json does not work by ZDu-IDM
* [#0294](https://github.com/InstituteforDiseaseModeling/idmtools/issues/294) - Docker containers failed to start if they are created but stopped by Clinton Collins
* [#0302](https://github.com/InstituteforDiseaseModeling/idmtools/issues/302) - Delete is broken by Clinton Collins
* [#0304](https://github.com/InstituteforDiseaseModeling/idmtools/issues/304) - Fix issue if failure during start of local platform the spinner continue to spin by Clinton Collins
* [#0323](https://github.com/InstituteforDiseaseModeling/idmtools/issues/323) - idmtools is not retro-compatible with pre-idmtools experiments by ckirkman-IDM
* [#0332](https://github.com/InstituteforDiseaseModeling/idmtools/issues/332) - with large number of simulations, local platform either timeout on dramatiq or stuck on persistamceService save method by Clinton Collins
* [#0339](https://github.com/InstituteforDiseaseModeling/idmtools/issues/339) - Analyzer tests fails on AnalyzeManager analyze len(self.potential_items) == 0 by ckirkman-IDM
* [#0341](https://github.com/InstituteforDiseaseModeling/idmtools/issues/341) - AnalyzeManager Runtime error on worker_pool by ckirkman-IDM
* [#0345](https://github.com/InstituteforDiseaseModeling/idmtools/issues/345) - PlatformFactory broken existing test in branch 'analyze-manager-port' by ckirkman-IDM
* [#0346](https://github.com/InstituteforDiseaseModeling/idmtools/issues/346) - UnknownItemException for analyzers on COMPSPlatform PythonExperiments by ckirkman-IDM
* [#0348](https://github.com/InstituteforDiseaseModeling/idmtools/issues/348) - DTKExperiment's pre_creation method should not hard coded Eradication extension to ".exe" by Benoit Raybaud
* [#0349](https://github.com/InstituteforDiseaseModeling/idmtools/issues/349) - Permission denied for local platform for DTKExperiment by Clinton Collins
* [#0350](https://github.com/InstituteforDiseaseModeling/idmtools/issues/350) - RunTask in local platform should catch exception by Clinton Collins
* [#0351](https://github.com/InstituteforDiseaseModeling/idmtools/issues/351) - AnalyzeManager finalize_results Process cannot access the cache.db because it is being used by another process by ckirkman-IDM
* [#0352](https://github.com/InstituteforDiseaseModeling/idmtools/issues/352) - Current structure of code leads to circular dependencies or classes as modules by Clinton Collins
* [#0375](https://github.com/InstituteforDiseaseModeling/idmtools/issues/375) - AnalyzerManager does not work for case to add experiment to analyzermanager by Benoit Raybaud
* [#0376](https://github.com/InstituteforDiseaseModeling/idmtools/issues/376) - AnalyzerManager does not work for simulation by Benoit Raybaud
* [#0378](https://github.com/InstituteforDiseaseModeling/idmtools/issues/378) - experiment/simulation display and print are messed up in latest dev by Benoit Raybaud
* [#0386](https://github.com/InstituteforDiseaseModeling/idmtools/issues/386) - Local platform cannot create more than 20 simulations in a given experiment by Benoit Raybaud
* [#0389](https://github.com/InstituteforDiseaseModeling/idmtools/issues/389) - Dev branch's docker repo is missing 0.2.0.nightly image which LocalPlatform needs by Clinton Collins
* [#0398](https://github.com/InstituteforDiseaseModeling/idmtools/issues/398) - Ensure that redis and postgres ports work as expected by Clinton Collins
* [#0425](https://github.com/InstituteforDiseaseModeling/idmtools/issues/425) - Idmtools should still support old Eradication.exe by Benoit Raybaud
* [#0426](https://github.com/InstituteforDiseaseModeling/idmtools/issues/426) - Need support to upload Eradication and everything else in same folder by Benoit Raybaud
* [#0427](https://github.com/InstituteforDiseaseModeling/idmtools/issues/427) - Access to the experiment object in analyzers by Benoit Raybaud
* [#0429](https://github.com/InstituteforDiseaseModeling/idmtools/issues/429) - Cleanup_cache fails PermissionError: [WinError 32] The process cannot access the file because it is being used by another process by Clinton Collins
* [#0431](https://github.com/InstituteforDiseaseModeling/idmtools/issues/431) - In linux_test_env for window, test_AnalyzeManager.py failed somecases by Clinton Collins
* [#0436](https://github.com/InstituteforDiseaseModeling/idmtools/issues/436) - Linux emod test fail by Clinton Collins
* [#0455](https://github.com/InstituteforDiseaseModeling/idmtools/issues/455) - Some tests randomly fail in idmtools_core by Clinton Collins
* [#0458](https://github.com/InstituteforDiseaseModeling/idmtools/issues/458) - There is no way to add custom tags to simulations by zdu
* [#0465](https://github.com/InstituteforDiseaseModeling/idmtools/issues/465) - BuilderExperiment for sweep "string" is wrong by zdu
* [#0560](https://github.com/InstituteforDiseaseModeling/idmtools/issues/560) - docker-compose build does not work for r-model example by Sharon Chen
* [#0562](https://github.com/InstituteforDiseaseModeling/idmtools/issues/562) - workflow_item_operations get workitem querycriteria fails by ZDu-IDM
* [#0572](https://github.com/InstituteforDiseaseModeling/idmtools/issues/572) - python 3.7.3 less version will fail for task type changing by Clinton Collins
* [#0585](https://github.com/InstituteforDiseaseModeling/idmtools/issues/585) - print(platform) throws exception for Python 3.6 by ZDu-IDM
* [#0588](https://github.com/InstituteforDiseaseModeling/idmtools/issues/588) - Running the dev installation in a virtualenv "installs" it globally by Clinton Collins
* [#0598](https://github.com/InstituteforDiseaseModeling/idmtools/issues/598) - CSVAnalyzer pass wrong value to parse in super().__init__ call by ZDu-IDM
* [#0602](https://github.com/InstituteforDiseaseModeling/idmtools/issues/602) - Analyzer doesn't work for my Python SEIR model by Clinton Collins
* [#0605](https://github.com/InstituteforDiseaseModeling/idmtools/issues/605) - When running multiple analyzers together, 'data' in one analyzer should not contains data from other analyzer by Clark Kirkman IV
* [#0608](https://github.com/InstituteforDiseaseModeling/idmtools/issues/608) - Can not add custom tag to AssetCollection in idmtools by zdu
* [#0616](https://github.com/InstituteforDiseaseModeling/idmtools/issues/616) - AssetCollection pre_creation failed if no tag by zdu
* [#0641](https://github.com/InstituteforDiseaseModeling/idmtools/issues/641) - Remove unused code in the python_requirements_ac by ZDu-IDM
* [#0643](https://github.com/InstituteforDiseaseModeling/idmtools/issues/643) - "pymake ssmt-image-local" in idmtools_platform_comps not working by Clinton Collins
* [#0644](https://github.com/InstituteforDiseaseModeling/idmtools/issues/644) - Platform cannot run workitem directly by zdu
* [#0646](https://github.com/InstituteforDiseaseModeling/idmtools/issues/646) - platform.get_items(ac) not return tags by zdu
* [#0661](https://github.com/InstituteforDiseaseModeling/idmtools/issues/661) - Code cleanup: removed dtk-tools references from import by Clinton Collins
* [#0670](https://github.com/InstituteforDiseaseModeling/idmtools/issues/670) - Disable Comps CLI for now since it is incomplete by Clinton Collins


Configuration
-------------
* [#0248](https://github.com/InstituteforDiseaseModeling/idmtools/issues/248) - Logging needs to support user configuration through the idmtools.ini by Sharon Chen
* [#0392](https://github.com/InstituteforDiseaseModeling/idmtools/issues/392) - Improve IdmConfigParser: make decorator for ensure_ini() method... by zdu
* [#0597](https://github.com/InstituteforDiseaseModeling/idmtools/issues/597) - Platform should not be case sensitive. by Clark Kirkman IV


Core
----
* [#0009](https://github.com/InstituteforDiseaseModeling/idmtools/issues/9) - Boilerplate command by Clinton Collins
* [#0081](https://github.com/InstituteforDiseaseModeling/idmtools/issues/81) - Allows the sweeps to be created in arms by zdu
* [#0084](https://github.com/InstituteforDiseaseModeling/idmtools/issues/84) - Explore different backend for object storage by Clinton Collins
* [#0091](https://github.com/InstituteforDiseaseModeling/idmtools/issues/91) - Refactor the Experiment/Simulation objects to not persist the simulations by Benoit Raybaud
* [#0110](https://github.com/InstituteforDiseaseModeling/idmtools/issues/110) - Explore event framework in the tools by Clinton Collins
* [#0118](https://github.com/InstituteforDiseaseModeling/idmtools/issues/118) - Add the printing of children in the EntityContainer by Benoit Raybaud
* [#0132](https://github.com/InstituteforDiseaseModeling/idmtools/issues/132) - The Experiment should be able to take a collection of builders instead of single object by zdu
* [#0141](https://github.com/InstituteforDiseaseModeling/idmtools/issues/141) - Standard Logging throughout tools by Clinton Collins
* [#0150](https://github.com/InstituteforDiseaseModeling/idmtools/issues/150) - missing pandas package by Benoit Raybaud
* [#0166](https://github.com/InstituteforDiseaseModeling/idmtools/issues/166) - docker-compose needs to in prerequisite  by Clinton Collins
* [#0169](https://github.com/InstituteforDiseaseModeling/idmtools/issues/169) - Handle 3.6 requirements automatically by Sharon Chen
* [#0177](https://github.com/InstituteforDiseaseModeling/idmtools/issues/177) - workflows: create a calibration mockup example by ckirkman-IDM
* [#0181](https://github.com/InstituteforDiseaseModeling/idmtools/issues/181) - Local Runner Docker image should be pre-built, stored in artifactory and have a quick-run ability by Clinton Collins
* [#0186](https://github.com/InstituteforDiseaseModeling/idmtools/issues/186) - The `local_runner` client should move to the `idmtools` package by Clinton Collins
* [#0187](https://github.com/InstituteforDiseaseModeling/idmtools/issues/187) - Move the CLI package to idmtools/cli by Sharon Chen
* [#0188](https://github.com/InstituteforDiseaseModeling/idmtools/issues/188) - Ensure the dependencies are moved from local_runner to idmtools by Sharon Chen
* [#0189](https://github.com/InstituteforDiseaseModeling/idmtools/issues/189) - Relies on the platform for the listing of simulations/experiments by Clinton Collins
* [#0190](https://github.com/InstituteforDiseaseModeling/idmtools/issues/190) - Add a platform attribute to the CLI commands by Sharon Chen
* [#0191](https://github.com/InstituteforDiseaseModeling/idmtools/issues/191) - Create a PlatformFactory by zdu
* [#0200](https://github.com/InstituteforDiseaseModeling/idmtools/issues/200) - Platforms should be plugins by Sharon Chen
* [#0201](https://github.com/InstituteforDiseaseModeling/idmtools/issues/201) - Update version code by ZDu-IDM
* [#0234](https://github.com/InstituteforDiseaseModeling/idmtools/issues/234) - Please add assets parameter to DTKExperiment by zdu
* [#0238](https://github.com/InstituteforDiseaseModeling/idmtools/issues/238) - Simulations of Experiment should be made pickle ignored by zdu
* [#0239](https://github.com/InstituteforDiseaseModeling/idmtools/issues/239) - Can we use same name for these 2 functions by zdu
* [#0241](https://github.com/InstituteforDiseaseModeling/idmtools/issues/241) - CLI should be distinct package and implement as plugins by Sharon Chen
* [#0242](https://github.com/InstituteforDiseaseModeling/idmtools/issues/242) - Please add loading config from file option to DTKExperiment by zdu
* [#0244](https://github.com/InstituteforDiseaseModeling/idmtools/issues/244) - Inputs values needs to be validated when creating a Platform by ZDu-IDM
* [#0251](https://github.com/InstituteforDiseaseModeling/idmtools/issues/251) - Setup for the CLI package should provide a entrypoint for easy use of commands by Sharon Chen
* [#0252](https://github.com/InstituteforDiseaseModeling/idmtools/issues/252) - Add --debug to cli main level by Clinton Collins
* [#0257](https://github.com/InstituteforDiseaseModeling/idmtools/issues/257) - CsvExperimentBuilder does not handle csv field with empty space by zdu
* [#0268](https://github.com/InstituteforDiseaseModeling/idmtools/issues/268) - demographics filenames should be loaded to asset collection by zdu
* [#0278](https://github.com/InstituteforDiseaseModeling/idmtools/issues/278) - DTK model is missing the way dynamically generate demographic file paths from config.json by ZDu-IDM
* [#0281](https://github.com/InstituteforDiseaseModeling/idmtools/issues/281) - Improve Platform to display selected Block info when creating a platform by zdu
* [#0297](https://github.com/InstituteforDiseaseModeling/idmtools/issues/297) - Fix issues with platform factory by zdu
* [#0307](https://github.com/InstituteforDiseaseModeling/idmtools/issues/307) - idmtools: Packages names should be consistent by Clinton Collins
* [#0315](https://github.com/InstituteforDiseaseModeling/idmtools/issues/315) - Basic support of suite in the tools by zdu
* [#0357](https://github.com/InstituteforDiseaseModeling/idmtools/issues/357) - ExperimentPersistService.save are not consistent by ZDu-IDM
* [#0358](https://github.com/InstituteforDiseaseModeling/idmtools/issues/358) - Improve Constructor of IExperiment by zdu
* [#0359](https://github.com/InstituteforDiseaseModeling/idmtools/issues/359) - SimulationPersistService is not used in Idmtools by ZDu-IDM
* [#0361](https://github.com/InstituteforDiseaseModeling/idmtools/issues/361) - assets in Experiment should be made "pickle-ignore" by ZDu-IDM
* [#0362](https://github.com/InstituteforDiseaseModeling/idmtools/issues/362) - base_simulation in Experiment should be made "pickle-ignore" by zdu
* [#0368](https://github.com/InstituteforDiseaseModeling/idmtools/issues/368) - PersistService should support clear() method by zdu
* [#0369](https://github.com/InstituteforDiseaseModeling/idmtools/issues/369) - The method create_simulations of Experiment should consider pre-defined max_workers and batch_size in idmtools.ini by zdu
* [#0370](https://github.com/InstituteforDiseaseModeling/idmtools/issues/370) - Add unit test for deepcopy on simulations by zdu
* [#0371](https://github.com/InstituteforDiseaseModeling/idmtools/issues/371) - Wrong type for platform_id in IEntity definition by zdu
* [#0372](https://github.com/InstituteforDiseaseModeling/idmtools/issues/372) - We may need to do code clean up after Analyzer stuff got merged into dev by Benoit Raybaud
* [#0391](https://github.com/InstituteforDiseaseModeling/idmtools/issues/391) - Improve Asset and AssetCollection classes by using @dataclass (field) for clear comparison by zdu
* [#0394](https://github.com/InstituteforDiseaseModeling/idmtools/issues/394) - Remove the ExperimentPersistService by Clinton Collins
* [#0438](https://github.com/InstituteforDiseaseModeling/idmtools/issues/438) - Support pulling Eradication from URLs and bamboo by Clinton Collins
* [#0449](https://github.com/InstituteforDiseaseModeling/idmtools/issues/449) - Investigate how we can frozen a class instance by zdu
* [#0518](https://github.com/InstituteforDiseaseModeling/idmtools/issues/518) - Add a task class. by Clinton Collins
* [#0520](https://github.com/InstituteforDiseaseModeling/idmtools/issues/520) - Rename current experiment builders to sweep builders by Clinton Collins
* [#0526](https://github.com/InstituteforDiseaseModeling/idmtools/issues/526) - Create New Generic Experiment Class by Clinton Collins
* [#0527](https://github.com/InstituteforDiseaseModeling/idmtools/issues/527) - Create new Generic Simulation Class by Clinton Collins
* [#0528](https://github.com/InstituteforDiseaseModeling/idmtools/issues/528) - Remove old Experiments/Simulations by Clinton Collins
* [#0529](https://github.com/InstituteforDiseaseModeling/idmtools/issues/529) - Create New Task API  by Clinton Collins
* [#0530](https://github.com/InstituteforDiseaseModeling/idmtools/issues/530) - Rename current model api to simulation/experiment API. by Clinton Collins
* [#0538](https://github.com/InstituteforDiseaseModeling/idmtools/issues/538) - Refactor platform interface into subinterfaces by Clinton Collins
* [#0633](https://github.com/InstituteforDiseaseModeling/idmtools/issues/633) - Test the packaging of release 1.0 by mfisher-idmod


Developer/Test
--------------
* [#0082](https://github.com/InstituteforDiseaseModeling/idmtools/issues/82) - Setup Bamboo on GitHub to run the tests by mfisher-idmod
* [#0104](https://github.com/InstituteforDiseaseModeling/idmtools/issues/104) - Test the fetching of children objects at runtime.  by Benoit Raybaud
* [#0117](https://github.com/InstituteforDiseaseModeling/idmtools/issues/117) - Create an environment variable to run the COMPS related tests or not by Benoit Raybaud
* [#0220](https://github.com/InstituteforDiseaseModeling/idmtools/issues/220) - Test case of test_direct_sweep_one_parameter_local in test_python_simulation.py should have fail status by Clinton Collins
* [#0631](https://github.com/InstituteforDiseaseModeling/idmtools/issues/631) - Ensure setup.py is consistent throughout by mfisher-idmod


Documentation
-------------
* [#0100](https://github.com/InstituteforDiseaseModeling/idmtools/issues/100) - Installation steps documented for users by JSchripsema-IDM
* [#0182](https://github.com/InstituteforDiseaseModeling/idmtools/issues/182) - Document procedure to use development libary withLocal Runner by Clinton Collins
* [#0312](https://github.com/InstituteforDiseaseModeling/idmtools/issues/312) - there is a typo in README by Clinton Collins
* [#0486](https://github.com/InstituteforDiseaseModeling/idmtools/issues/486) - Overview of the analysis in idmtools by Clinton Collins
* [#0578](https://github.com/InstituteforDiseaseModeling/idmtools/issues/578) - Add installation for users  by JSchripsema-IDM
* [#0593](https://github.com/InstituteforDiseaseModeling/idmtools/issues/593) - Simple Python SEIR model demo example  by Clinton Collins
* [#0632](https://github.com/InstituteforDiseaseModeling/idmtools/issues/632) - Update idmtools_core setup.py to remove model emod from idm install by Clinton Collins


Feature Request
---------------
* [#0233](https://github.com/InstituteforDiseaseModeling/idmtools/issues/233) - Should give flexibility for local runner timeout by Sharon Chen
* [#0603](https://github.com/InstituteforDiseaseModeling/idmtools/issues/603) - implement install custom requirement libs to asset collection with WorkItem by zdu


Models
------
* [#0024](https://github.com/InstituteforDiseaseModeling/idmtools/issues/24) - R Model support by Clinton Collins
* [#0053](https://github.com/InstituteforDiseaseModeling/idmtools/issues/53) - Support of demographics files by Benoit Raybaud
* [#0113](https://github.com/InstituteforDiseaseModeling/idmtools/issues/113) - Create a draft DTKConfigBuilder equivalent  by Benoit Raybaud
* [#0212](https://github.com/InstituteforDiseaseModeling/idmtools/issues/212) - Models should be plugins by Clinton Collins
* [#0235](https://github.com/InstituteforDiseaseModeling/idmtools/issues/235) - Please add update bulk updates for config/campaign parameters to DTKSimulation  by zdu
* [#0287](https://github.com/InstituteforDiseaseModeling/idmtools/issues/287) - Add info about support models/docker support to platform by Clinton Collins
* [#0288](https://github.com/InstituteforDiseaseModeling/idmtools/issues/288) - Create DockerExperiment and subclasses by Clinton Collins
* [#0519](https://github.com/InstituteforDiseaseModeling/idmtools/issues/519) - Move experiment building to ExperimentBuilder by Clinton Collins
* [#0521](https://github.com/InstituteforDiseaseModeling/idmtools/issues/521) - Create Generic Dictionary Config Task by Clinton Collins
* [#0522](https://github.com/InstituteforDiseaseModeling/idmtools/issues/522) - Create PythonTask by Clinton Collins
* [#0523](https://github.com/InstituteforDiseaseModeling/idmtools/issues/523) - Create PythonDictionaryTask by Clinton Collins
* [#0524](https://github.com/InstituteforDiseaseModeling/idmtools/issues/524) - Create RTask by Clinton Collins
* [#0525](https://github.com/InstituteforDiseaseModeling/idmtools/issues/525) - Create EModTask by Clinton Collins
* [#0535](https://github.com/InstituteforDiseaseModeling/idmtools/issues/535) - Create DockerTask by Clinton Collins


Platforms
---------
* [#0027](https://github.com/InstituteforDiseaseModeling/idmtools/issues/27) - SSMT Platform by Benoit Raybaud
* [#0072](https://github.com/InstituteforDiseaseModeling/idmtools/issues/72) - [Local Runner] Cancelling capabilities by Clinton Collins
* [#0094](https://github.com/InstituteforDiseaseModeling/idmtools/issues/94) - Batch and parallelize simulation creation in the COMPSPlatform by Benoit Raybaud
* [#0122](https://github.com/InstituteforDiseaseModeling/idmtools/issues/122) - Ability to create an AssetCollection based on a COMPS asset collection id by Clinton Collins
* [#0130](https://github.com/InstituteforDiseaseModeling/idmtools/issues/130) - User configuration and data storage location by Clinton Collins
* [#0194](https://github.com/InstituteforDiseaseModeling/idmtools/issues/194) - COMPS Files retrieval system by Benoit Raybaud
* [#0195](https://github.com/InstituteforDiseaseModeling/idmtools/issues/195) - LOCAL Files retrieval system by Clinton Collins
* [#0221](https://github.com/InstituteforDiseaseModeling/idmtools/issues/221) - Local runner for experiment/simulations have different file hierarchy than COMPS  by Clinton Collins
* [#0254](https://github.com/InstituteforDiseaseModeling/idmtools/issues/254) - Local Platform Assest should be implemented via API or Docker socket by Sharon Chen
* [#0264](https://github.com/InstituteforDiseaseModeling/idmtools/issues/264) - idmtools_local_runner's tasks/run.py should have better handle for unhandled exception by Sharon Chen
* [#0276](https://github.com/InstituteforDiseaseModeling/idmtools/issues/276) - Docker services should be started for end-users without needing to use docker-compose by Sharon Chen
* [#0280](https://github.com/InstituteforDiseaseModeling/idmtools/issues/280) - Generalize sim/exp/suite format of ISimulation, IExperiment, IPlatform by ckirkman-IDM
* [#0286](https://github.com/InstituteforDiseaseModeling/idmtools/issues/286) - Add special GPU queue to Local Platform by Clinton Collins
* [#0306](https://github.com/InstituteforDiseaseModeling/idmtools/issues/306) - AssetCollection's assets_from_directory logic wrong if set flatten and relative path at same time by Benoit Raybaud
* [#0310](https://github.com/InstituteforDiseaseModeling/idmtools/issues/310) - idmtools: make use field in LocalPlatform definition by Benoit Raybaud
* [#0316](https://github.com/InstituteforDiseaseModeling/idmtools/issues/316) - Integrate website with Local Runner Container by Clinton Collins
* [#0329](https://github.com/InstituteforDiseaseModeling/idmtools/issues/329) - Experiment level status by Benoit Raybaud
* [#0330](https://github.com/InstituteforDiseaseModeling/idmtools/issues/330) - Paging on simulation/experiment APIs for better UI experience by Clinton Collins
* [#0333](https://github.com/InstituteforDiseaseModeling/idmtools/issues/333) - ensure pyComps allows comptabilite releases  by Clinton Collins
* [#0347](https://github.com/InstituteforDiseaseModeling/idmtools/issues/347) - there is no failed case show up in idmtools_webui for experiment by David Kong
* [#0364](https://github.com/InstituteforDiseaseModeling/idmtools/issues/364) - Local platform should use production artfactory for docker images by Clinton Collins
* [#0381](https://github.com/InstituteforDiseaseModeling/idmtools/issues/381) - Support Work Items in COMPS Platform by ZDu-IDM
* [#0387](https://github.com/InstituteforDiseaseModeling/idmtools/issues/387) - Local platform webUI only show simulations up to 20 by Clinton Collins
* [#0393](https://github.com/InstituteforDiseaseModeling/idmtools/issues/393) - local platform tests keep getting EOFError while logger is in DEBUG and console is on by Sharon Chen
* [#0395](https://github.com/InstituteforDiseaseModeling/idmtools/issues/395) - Remove parent_id and platform concepts from isimulation by Benoit Raybaud
* [#0405](https://github.com/InstituteforDiseaseModeling/idmtools/issues/405) - Support analysis of data from Work Items in Analyze Manager by zdu
* [#0407](https://github.com/InstituteforDiseaseModeling/idmtools/issues/407) - Support Service Side Analysis through SSMT by ZDu-IDM
* [#0437](https://github.com/InstituteforDiseaseModeling/idmtools/issues/437) - We should prompt users for docker credentials when not available by Clinton Collins
* [#0447](https://github.com/InstituteforDiseaseModeling/idmtools/issues/447) - Set limitation for docker container's access to memory by mfisher-idmod
* [#0532](https://github.com/InstituteforDiseaseModeling/idmtools/issues/532) - Make updates to ExperimentManager/Platform to support tasks by Clinton Collins
* [#0540](https://github.com/InstituteforDiseaseModeling/idmtools/issues/540) - Create initial SSMT Plaform from COMPS Platform by Clinton Collins
* [#0557](https://github.com/InstituteforDiseaseModeling/idmtools/issues/557) - Develop IDMTools docker image for SSMT by Clinton Collins
* [#0596](https://github.com/InstituteforDiseaseModeling/idmtools/issues/596) - COMPSPlatform.get_files(item,..) not working for Experiment or Suite by ZDu-IDM
* [#0635](https://github.com/InstituteforDiseaseModeling/idmtools/issues/635) - Update SSMT base image by Clinton Collins
* [#0639](https://github.com/InstituteforDiseaseModeling/idmtools/issues/639) - Add a way for the python_requirements_ac to use additional wheel file by zdu
* [#0676](https://github.com/InstituteforDiseaseModeling/idmtools/issues/676) - ssmt mising QueryCriteria support by zdu
* [#0677](https://github.com/InstituteforDiseaseModeling/idmtools/issues/677) - ssmt: refresh_status returns None by ZDu-IDM


User Experience
---------------
* [#0457](https://github.com/InstituteforDiseaseModeling/idmtools/issues/457) - Option to analyze failed simulations by Clinton Collins
