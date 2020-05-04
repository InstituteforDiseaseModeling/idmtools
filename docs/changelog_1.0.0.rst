
=====
1.0.0
=====


Additional Changes
------------------
* [#0104](https://github.com/InstituteforDiseaseModeling/idmtools/issues/104) - Test the fetching of children objects at runtime.  by Benoit Raybaud
* [#0117](https://github.com/InstituteforDiseaseModeling/idmtools/issues/117) - Create an environment variable to run the COMPS related tests or not by Benoit Raybaud
* [#0160](https://github.com/InstituteforDiseaseModeling/idmtools/issues/160) - Update tests and add more validations by Sharon Chen
* [#0220](https://github.com/InstituteforDiseaseModeling/idmtools/issues/220) - Testcase of test_direct_sweep_one_parameter_local in test_python_simulation.py should have fail status by Clinton Collins
* [#0223](https://github.com/InstituteforDiseaseModeling/idmtools/issues/223) - UnicodeDecodeError for testcases in test_dtk.py when run with LocalPlatform by Clinton Collins
* [#0237](https://github.com/InstituteforDiseaseModeling/idmtools/issues/237) - Add basic examples how to generate simulations with parameter update and sweep parameters, also add local runner tests by Sharon Chen
* [#0253](https://github.com/InstituteforDiseaseModeling/idmtools/issues/253) - fix failed testcase in test_python_simulation.py after dev fixed loca… by Sharon Chen
* [#0352](https://github.com/InstituteforDiseaseModeling/idmtools/issues/352) - Current structure of code leads to circular dependencies or classes as modules by Clinton Collins
* [#0377](https://github.com/InstituteforDiseaseModeling/idmtools/issues/377) - Fix few dtk->emod missing places in current dev by Sharon Chen
* [#0573](https://github.com/InstituteforDiseaseModeling/idmtools/issues/573) - Reorganizing example's folder names by Sharon Chen
* [#0577](https://github.com/InstituteforDiseaseModeling/idmtools/issues/577) - Add few more python model examples by Sharon Chen
* [#0581](https://github.com/InstituteforDiseaseModeling/idmtools/issues/581) - New general purpose analyzers with examples and tests by mfisher-idmod
* [#0587](https://github.com/InstituteforDiseaseModeling/idmtools/issues/587) - Support SSMT in Idmtools by ZDu-IDM
* [#0604](https://github.com/InstituteforDiseaseModeling/idmtools/issues/604) - Develop IDMTools docker image for SSMT by Clinton Collins
* [#0607](https://github.com/InstituteforDiseaseModeling/idmtools/issues/607) - Script to filter sims by ZDu-IDM
* [#0612](https://github.com/InstituteforDiseaseModeling/idmtools/issues/612) - Ssmt test fix by Sharon Chen
* [#0649](https://github.com/InstituteforDiseaseModeling/idmtools/issues/649) - covid_abm support on SSMT by Benoit Raybaud
* [#0676](https://github.com/InstituteforDiseaseModeling/idmtools/issues/676) - ssmt mising QueryCriteria support by zdu
* [#0686](https://github.com/InstituteforDiseaseModeling/idmtools/issues/686) - Remove covid_abm examples by Benoit Raybaud


Bugs
----
* [#0124](https://github.com/InstituteforDiseaseModeling/idmtools/issues/124) - Can not run tests\test_python_simulation.py from console by Benoit Raybaud
* [#0125](https://github.com/InstituteforDiseaseModeling/idmtools/issues/125) - relative_path for AssetCollection does not work by Benoit Raybaud
* [#0129](https://github.com/InstituteforDiseaseModeling/idmtools/issues/129) - new python model root node changed from "config" to "parameters" by Benoit Raybaud
* [#0142](https://github.com/InstituteforDiseaseModeling/idmtools/issues/142) - experiment.batch_simulations seems not doing batch by Benoit Raybaud
* [#0143](https://github.com/InstituteforDiseaseModeling/idmtools/issues/143) - COMPSPlatform's refresh_experiment_status() get called too much from ExperimentManager's wait_till_done() mathod by Benoit Raybaud
* [#0170](https://github.com/InstituteforDiseaseModeling/idmtools/issues/170) - tag "type: idmtools_models.python.PythonExperiment" can be missing for same test by Benoit Raybaud
* [#0184](https://github.com/InstituteforDiseaseModeling/idmtools/issues/184) - Missing 'data' dir for test_experiment_manager test. (TestPlatform) by zdu
* [#0228](https://github.com/InstituteforDiseaseModeling/idmtools/issues/228) - Fix-194 is still not working for python 3.6 in Linux by Benoit Raybaud
* [#0247](https://github.com/InstituteforDiseaseModeling/idmtools/issues/247) - Fix update config parameters by using get/set functions instead directly call config parameter by Sharon Chen
* [#0258](https://github.com/InstituteforDiseaseModeling/idmtools/issues/258) - fix typo from previous checkin by Sharon Chen
* [#0294](https://github.com/InstituteforDiseaseModeling/idmtools/issues/294) - Docker containers failed to start if they are created but stopped by Clinton Collins
* [#0304](https://github.com/InstituteforDiseaseModeling/idmtools/issues/304) - Fix issue if failure during start of local platform the spinner continue to spin by Clinton Collins
* [#0332](https://github.com/InstituteforDiseaseModeling/idmtools/issues/332) - with large number of simulations, local platform either timeout on dramatiq or stuck on persistamceService save method by Clinton Collins
* [#0386](https://github.com/InstituteforDiseaseModeling/idmtools/issues/386) - Local platfrom cannot create more than 20 simulations in a given experiment by Benoit Raybaud
* [#0396](https://github.com/InstituteforDiseaseModeling/idmtools/issues/396) - fix population analyzer test which failed in linux in bamboo by Sharon Chen
* [#0425](https://github.com/InstituteforDiseaseModeling/idmtools/issues/425) - Idmtools should still support old Eradication.exe by Benoit Raybaud
* [#0426](https://github.com/InstituteforDiseaseModeling/idmtools/issues/426) - Need support to upload Eradication and everything else in same folder by Benoit Raybaud
* [#0427](https://github.com/InstituteforDiseaseModeling/idmtools/issues/427) - Access to the experiment object in analyzers by Benoit Raybaud
* [#0455](https://github.com/InstituteforDiseaseModeling/idmtools/issues/455) - Some tests randomly fail in idmtools_core by Clinton Collins
* [#0458](https://github.com/InstituteforDiseaseModeling/idmtools/issues/458) - There is no way to add custom tags to simulations by zdu
* [#0465](https://github.com/InstituteforDiseaseModeling/idmtools/issues/465) - BuilderExperiment for sweep "string" is wrong by zdu
* [#0572](https://github.com/InstituteforDiseaseModeling/idmtools/issues/572) - python 3.7.3 less version will fail for task type changing by Clinton Collins
* [#0576](https://github.com/InstituteforDiseaseModeling/idmtools/issues/576) - Fix failed test case with wrong import from previous PR by Sharon Chen
* [#0588](https://github.com/InstituteforDiseaseModeling/idmtools/issues/588) - Running the dev installation in a virtualenv "installs" it globally by Clinton Collins
* [#0605](https://github.com/InstituteforDiseaseModeling/idmtools/issues/605) - When running multiple analyzers together, 'data' in one analyzer should not contains data from other analyzer by Clark Kirkman IV
* [#0608](https://github.com/InstituteforDiseaseModeling/idmtools/issues/608) - Can not add custom tag to AssetCollection in idmtools by zdu
* [#0616](https://github.com/InstituteforDiseaseModeling/idmtools/issues/616) - AssetCollection pre_creation failed if no tag by zdu
* [#0643](https://github.com/InstituteforDiseaseModeling/idmtools/issues/643) - "pymake ssmt-image-local" in idmtools_platform_comps not working by Clinton Collins
* [#0644](https://github.com/InstituteforDiseaseModeling/idmtools/issues/644) - Platform cannot run workitem directly by zdu
* [#0646](https://github.com/InstituteforDiseaseModeling/idmtools/issues/646) - platform.get_items(ac) not return tags by zdu
* [#0661](https://github.com/InstituteforDiseaseModeling/idmtools/issues/661) - Code cleanup: removed dtk-tools references from import by Clinton Collins


Core
----
* [#0081](https://github.com/InstituteforDiseaseModeling/idmtools/issues/81) - Allows the sweeps to be created in arms by zdu
* [#0084](https://github.com/InstituteforDiseaseModeling/idmtools/issues/84) - Explore different backend for object storage by Clinton Collins
* [#0091](https://github.com/InstituteforDiseaseModeling/idmtools/issues/91) - Refactor the Experiment/Simulation objects to not persist the simulations by Benoit Raybaud
* [#0113](https://github.com/InstituteforDiseaseModeling/idmtools/issues/113) - Create a draft DTKConfigBuilder equivalent  by Benoit Raybaud
* [#0118](https://github.com/InstituteforDiseaseModeling/idmtools/issues/118) - Add the printing of children in the EntityContainer by Benoit Raybaud
* [#0132](https://github.com/InstituteforDiseaseModeling/idmtools/issues/132) - The Experiment should be able to take a collection of builders instead of single object by zdu
* [#0141](https://github.com/InstituteforDiseaseModeling/idmtools/issues/141) - Standard Logging throughout tools by Clinton Collins
* [#0150](https://github.com/InstituteforDiseaseModeling/idmtools/issues/150) - missing pandas package by Benoit Raybaud
* [#0191](https://github.com/InstituteforDiseaseModeling/idmtools/issues/191) - Create a PlatformFactory by zdu
* [#0212](https://github.com/InstituteforDiseaseModeling/idmtools/issues/212) - Models should be plugins by Clinton Collins
* [#0234](https://github.com/InstituteforDiseaseModeling/idmtools/issues/234) - Please add assets parameter to DTKExperiment by zdu
* [#0235](https://github.com/InstituteforDiseaseModeling/idmtools/issues/235) - Please add update bulk updates for config/campaign parameters to DTKSimulation  by zdu
* [#0238](https://github.com/InstituteforDiseaseModeling/idmtools/issues/238) - Simulations of Experiment should be made pickle ignored by zdu
* [#0239](https://github.com/InstituteforDiseaseModeling/idmtools/issues/239) - Can we use same name for these 2 functions by zdu
* [#0242](https://github.com/InstituteforDiseaseModeling/idmtools/issues/242) - Please add loading config from file option to DTKExperiment by zdu
* [#0252](https://github.com/InstituteforDiseaseModeling/idmtools/issues/252) - Add --debug to cli main level by Clinton Collins
* [#0257](https://github.com/InstituteforDiseaseModeling/idmtools/issues/257) - CsvExperimentBuilder does not handle csv field with empty space by zdu
* [#0268](https://github.com/InstituteforDiseaseModeling/idmtools/issues/268) - demographics filenames should be loaded to asset collection by zdu
* [#0281](https://github.com/InstituteforDiseaseModeling/idmtools/issues/281) - Improve Platform to display selected Block info when creating a platform by zdu
* [#0282](https://github.com/InstituteforDiseaseModeling/idmtools/issues/282) - Add unit and basic end-to-end tests for AnalyzeManager class by ckirkman-IDM
* [#0297](https://github.com/InstituteforDiseaseModeling/idmtools/issues/297) - Fix issues with platform factory by zdu
* [#0307](https://github.com/InstituteforDiseaseModeling/idmtools/issues/307) - idmtools: Packages names should be consistent by Clinton Collins
* [#0315](https://github.com/InstituteforDiseaseModeling/idmtools/issues/315) - Basic support of suite in the tools by zdu
* [#0358](https://github.com/InstituteforDiseaseModeling/idmtools/issues/358) - Improve Constructor of IExperiment by zdu
* [#0362](https://github.com/InstituteforDiseaseModeling/idmtools/issues/362) - base_simulation in Experiment should be made "pickle-ignore" by zdu
* [#0368](https://github.com/InstituteforDiseaseModeling/idmtools/issues/368) - PersistService should support clear() method by zdu
* [#0369](https://github.com/InstituteforDiseaseModeling/idmtools/issues/369) - The method create_simulations of Experiment should consider pre-defined max_workers and batch_size in idmtools.ini by zdu
* [#0370](https://github.com/InstituteforDiseaseModeling/idmtools/issues/370) - Add unit test for deepcopy on simulations by zdu
* [#0371](https://github.com/InstituteforDiseaseModeling/idmtools/issues/371) - Wrong type for platform_id in IEntity definition by zdu
* [#0391](https://github.com/InstituteforDiseaseModeling/idmtools/issues/391) - Improve Asset and AssetCollection classes by using @dataclass (field) for clear comparison by zdu
* [#0392](https://github.com/InstituteforDiseaseModeling/idmtools/issues/392) - Improve IdmConfigParser: make decorator for ensure_ini() method... by zdu
* [#0394](https://github.com/InstituteforDiseaseModeling/idmtools/issues/394) - Remove the ExperimentPersistService by Clinton Collins
* [#0449](https://github.com/InstituteforDiseaseModeling/idmtools/issues/449) - Investigate how we can frozen a class instance by zdu
* [#0518](https://github.com/InstituteforDiseaseModeling/idmtools/issues/518) - Add a task class. by Clinton Collins
* [#0521](https://github.com/InstituteforDiseaseModeling/idmtools/issues/521) - Create Generic Dictionary Config Task by Clinton Collins
* [#0524](https://github.com/InstituteforDiseaseModeling/idmtools/issues/524) - Create RTask by Clinton Collins
* [#0538](https://github.com/InstituteforDiseaseModeling/idmtools/issues/538) - Refactor platform interface into subinterfaces by Clinton Collins
* [#0590](https://github.com/InstituteforDiseaseModeling/idmtools/issues/590) - Refactor model to task by Clinton Collins
* [#0597](https://github.com/InstituteforDiseaseModeling/idmtools/issues/597) - Platform should not be case sensitive. by Clark Kirkman IV
* [#0614](https://github.com/InstituteforDiseaseModeling/idmtools/issues/614) - Convenience function to exclude items in analyze manager by Clark Kirkman IV
* [#0619](https://github.com/InstituteforDiseaseModeling/idmtools/issues/619) - Ability to get exp sim object ids in analyzers by Clark Kirkman IV


Developer/Test
--------------
* [#0259](https://github.com/InstituteforDiseaseModeling/idmtools/issues/259) - update setup test script to include create docker network there in case it is not created by Sharon Chen
* [#0259](https://github.com/InstituteforDiseaseModeling/idmtools/issues/259) - update setup test script to include create docker network there in case it is not created by zdu
* [#0383](https://github.com/InstituteforDiseaseModeling/idmtools/issues/383) - Add a developer container to run linux on Windows by Clinton Collins


Documentation
-------------
* [#0312](https://github.com/InstituteforDiseaseModeling/idmtools/issues/312) - idmtools: there is a typo in README by Clinton Collins


Feature Request
---------------
* [#0603](https://github.com/InstituteforDiseaseModeling/idmtools/issues/603) - implement install custom requirement libs to asset collection with WorkItem by zdu


Platforms
---------
* [#0072](https://github.com/InstituteforDiseaseModeling/idmtools/issues/72) - [Local Runner] Cancelling capabilities by Clinton Collins
* [#0094](https://github.com/InstituteforDiseaseModeling/idmtools/issues/94) - Batch and parallelize simulation creation in the COMPSPlatform by Benoit Raybaud
* [#0122](https://github.com/InstituteforDiseaseModeling/idmtools/issues/122) - Ability to create an AssetCollection based on a COMPS asset collection id by Clinton Collins
* [#0130](https://github.com/InstituteforDiseaseModeling/idmtools/issues/130) - User configuration and data storage location by Clinton Collins
* [#0194](https://github.com/InstituteforDiseaseModeling/idmtools/issues/194) - COMPS Files retrieval system by Benoit Raybaud
* [#0195](https://github.com/InstituteforDiseaseModeling/idmtools/issues/195) - LOCAL Files retrieval system by Clinton Collins
* [#0306](https://github.com/InstituteforDiseaseModeling/idmtools/issues/306) - AssetCollection's assets_from_directory logic wrong if set flatten and relative path at same time by Benoit Raybaud
* [#0310](https://github.com/InstituteforDiseaseModeling/idmtools/issues/310) - idmtools: make use field in LocalPlatform definition by Benoit Raybaud
* [#0316](https://github.com/InstituteforDiseaseModeling/idmtools/issues/316) - Integrate website with Local Runner Container by Clinton Collins
* [#0405](https://github.com/InstituteforDiseaseModeling/idmtools/issues/405) - Support analysis of data from Work Items in Analyze Manager by zdu
* [#0635](https://github.com/InstituteforDiseaseModeling/idmtools/issues/635) - Update SSMT base image by Clinton Collins
* [#0639](https://github.com/InstituteforDiseaseModeling/idmtools/issues/639) - Add a way for the python_requirements_ac to use additional wheel file by zdu


User Experience
---------------
* [#0457](https://github.com/InstituteforDiseaseModeling/idmtools/issues/457) - Option to analyze failed simulations by Clinton Collins
