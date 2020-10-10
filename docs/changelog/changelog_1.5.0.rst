=====
1.5.0
=====


Bugs
----
* `#0459 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/459>`_ - There is no way to add simulations to existing experiment
* `#0840 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/840>`_ - Experiment and Suite statuses not updated properly after success
* `#0841 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/841>`_ - Reloaded experiments and simulations have incorrect status
* `#0842 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/842>`_ - Reloaded simulations (likely all children) do not have their platform set
* `#0866 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/866>`_ - Recursive simulation loading bug
* `#0898 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/898>`_ - Update Experiment#add_new_simulations() to accept additions in any state
* `#1046 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1046>`_ - print(ac) cause maximum recursion depth exceeded while calling a Python object
* `#1047 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1047>`_ - datetime type is missing from IDMJSONEncoder
* `#1048 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1048>`_ - typo/bug: cols.append(cols)
* `#1049 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1049>`_ - The text should be generic not specific to asset collection in method from_id(...)
* `#1066 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1066>`_ - User logging should still be initialized if missing_ok is supplied when loading configuration/platform
* `#1071 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1071>`_ - Detect if an experiment needs commissioning
* `#1076 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1076>`_ - wi_ac create ac with tag wrong for Calculon
* `#1094 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1094>`_ - AssetCollection should check checksums when checking for duplicates
* `#1098 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1098>`_ - Add experiment id to CSVAnalyzer and TagAnalyzer


Dependencies
------------
* `#1075 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1075>`_ - Update sphinx requirement from ~=3.2.0 to ~=3.2.1
* `#1077 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1077>`_ - Update sqlalchemy requirement from ~=1.3.18 to ~=1.3.19
* `#1078 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1078>`_ - Update pygithub requirement from ~=1.52 to ~=1.53
* `#1080 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1080>`_ - Bump docker from 4.3.0 to 4.3.1
* `#1087 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1087>`_ - Update more-itertools requirement from ~=8.4.0 to ~=8.5.0
* `#1088 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1088>`_ - Update paramiko requirement from ~=2.7.1 to ~=2.7.2
* `#1101 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1101>`_ - Update psycopg2-binary requirement from ~=2.8.5 to ~=2.8.6
* `#1102 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1102>`_ - Bump pandas from 1.1.1 to 1.1.2
* `#1103 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1103>`_ - Bump diskcache from 5.0.2 to 5.0.3
* `#1107 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1107>`_ - Update tqdm requirement from ~=4.48.2 to ~=4.49.0
* `#1108 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1108>`_ - Update pytest requirement from ~=6.0.1 to ~=6.0.2


Documentation
-------------
* `#1073 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1073>`_ - Update example and tests to use platform context


Feature Request
---------------
* `#1064 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1064>`_ - Allow running without a idmtools.ini file
* `#1068 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1068>`_ - COMPPlatform should allow commissioning as it goes
