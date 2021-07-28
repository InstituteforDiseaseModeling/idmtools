=====
1.5.1
=====


1.5.1 - Bugs
------------
* `#1166 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1166>`_ - Properly remove/replace unsupported characters on the COMPS platform in experiment names
* `#1173 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1173>`_ - Ensure assets are not directories on creation of Asset


1.5.1 - Documentation
---------------------
* `#1191 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1191>`_ - Remove idmtools.ini from examples to leverage configuration aliases. This change allows executing of examples with minimal local configuration


1.5.1 - Feature Request
-----------------------
* `#1127 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1127>`_ - Remove emodpy from idmtools[full] and idmtools[idm] install options. This allows a more control of packages used in projects
* `#1179 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1179>`_ - Supply multiple default templates for template script wrapper. See the examples in the cookbook.
* `#1180 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1180>`_ - Support Configuration Aliases. This provides out of the box configurations for common platform configurations. For example, COMPS environments have predefined aliases such as Calculon, Belegost, etc


1.5.1 -  Known Issues
---------------------
* PlatformAnalysis requires an idmtools.ini


1.5.1 - Upcoming breaking changes in 1.6.0
------------------------------------------
* Assets will no longer support both absolute_path and content. That will be mutually exclusive going forward
* The task API **pre_creation** method has a new parameter to pass the platform object. All tasks implementing the API will need to update the pre_creation method
* Deprecation of the *delete* function from *AssetCollection* in favor or *remove*.


1.5.1 - Upcoming features in the coming releases
------------------------------------------------
* Ability to query the platform from task for items such as OS, supported workflows, etc
* Utility to Asset-ize outputs within COMPS. This should make it into 1.6.0
* HPC Container build and run utilities. Slated for next few releases
* Better integration of errors with references to relevant documentation(ongoing)
* Improves support for Mac OS
