=====
1.6.0
=====


Bugs
----
* `#0300 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/300>`_ - Canceling simulations using cli's Restful api throws Internal server error (Local Platform)
* `#0462 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/462>`_ - Redis port configuration not working (Local Platform)
* `#0988 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/988>`_ - Fix issues with multi-threading and requests on mac in python 3.7 or lower
* `#1104 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1104>`_ - Run AnalyzeManager outputs ini file used multiple times
* `#1111 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1111>`_ - File path missing in logger messages when level set to INFO
* `#1154 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1154>`_ - Add option for experiment run in COMPS to use the minimal execution path
* `#1156 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1156>`_ - COMPS should dynamically add Windows and LINUX Requirements based on environments
* `#1195 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1195>`_ - PlatformAnalysis should support aliases as well
* `#1198 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1198>`_ - PlatformAnalysis should detect should find user's idmtools.ini instead of searching current directory
* `#1230 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1230>`_ - Fix parsing of executable on commandline
* `#1244 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1244>`_ - Logging should fall back to console if the log file cannot be opened


CLI
---
* `#1167 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1167>`_ - idmtools config CLI command should have option to use global path
* `#1237 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1237>`_ - Add ability to suppress outputs for CLI commands that might generate pipe-able output
* `#1234 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1234>`_ - Add AssetizeOutputs as COMPS Cli command
* `#1236 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1236>`_ - Add COMPS Login command to CLI


Configuration
-------------
* `#1242 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1242>`_ - Enable loading configuration options from environment variables


Core
----
* `#0571 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/571>`_ - Support multi-cores(MPI) on COMPS through num_cores
* `#1220 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1220>`_ - Workflow items should use name
* `#1221 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1221>`_ - Workflow items should use Assets instead of asset_collection_id
* `#1222 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1222>`_ - Workflow items should use transient assets vs user_files
* `#1223 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1223>`_ - Commands from WorkflowItems should support Tasks
* `#1224 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1224>`_ - Support creating AssetCollection from list of file paths


Dependencies
------------
* `#1136 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1136>`_ - Remove marshmallow as a dependency
* `#1207 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1207>`_ - Update pytest requirement from ~=6.1.0 to ~=6.1.1
* `#1209 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1209>`_ - Update flake8 requirement from ~=3.8.3 to ~=3.8.4
* `#1211 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1211>`_ - Bump pandas from 1.1.2 to 1.1.3
* `#1214 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1214>`_ - Update bump2version requirement from ~=1.0.0 to ~=1.0.1
* `#1216 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1216>`_ - Update tqdm requirement from ~=4.50.0 to ~=4.50.2
* `#1226 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1226>`_ - Update pycomps requirement from ~=2.3.8 to ~=2.3.9
* `#1227 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1227>`_ - Update sqlalchemy requirement from ~=1.3.19 to ~=1.3.20
* `#1228 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1228>`_ - Update colorama requirement from ~=0.4.1 to ~=0.4.4
* `#1246 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1246>`_ - Update yaspin requirement from ~=1.1.0 to ~=1.2.0
* `#1251 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1251>`_ - Update junitparser requirement from ~=1.4.1 to ~=1.4.2


Documentation
-------------
* `#1134 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1134>`_ - Add a copy to clipboard option to source code and command line examples in documentation


Feature Request
---------------
* `#1121 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1121>`_ - Experiment should error if no simulations are defined
* `#1148 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1148>`_ - Support global configuration file for idmtools from user home directory/local app directory or specified using an Environment Variable
* `#1158 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1158>`_ - Pass platform to pre_creation and post_creation methods to allow dynamic querying from platform
* `#1193 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1193>`_ - Support Asset-izing Outputs through WorkItems
* `#1194 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1194>`_ - Add support for post_creation hooks on Experiments/Simulation/Workitems
* `#1231 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1231>`_ - Allow setting command from string on Task
* `#1232 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1232>`_ - Add a function to determine if target is Windows to platform
* `#1233 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1233>`_ - Add property to grab the common asset path from a platform
* `#1247 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1247>`_ - Add support for singularity to the local platform


Platforms
---------
* `#0230 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/230>`_ - Entities should support created_on/modified_on fields on the Local Platform
* `#0324 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/324>`_ - Detect changes to Local Platform config


User Experience
---------------
* `#1127 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1127>`_ - IDMtools install should not include emodpy, emodapi, etc when installing with idmtools[full]
* `#1141 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1141>`_ - Add warning when user is using a development version of idmtools
* `#1160 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1160>`_ - get_script_wrapper_unix_task should use default template that adds assets to python path
* `#1200 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1200>`_ - Log idmtools core version when in debug mode
* `#1240 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1240>`_ - Give clear units for progress bars
* `#1241 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1241>`_ - Support disabling progress bars with environment variable or config


Special Notes
=====================
* If you encounter an issue with matplotlib after install, you may need to run `pip install matplotlib --force-reinstall`
* Workitems will require a Task starting in 1.7.0
* Containers support on COMPS and early singularity support will be coming in 1.6.1