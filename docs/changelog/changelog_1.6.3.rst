=====
1.6.3
=====


Bugs
----
* `#1396 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1396>`_ - requirements to ac should default to one core
* `#1403 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1403>`_ - Progress bar displayed when expecting only json on AssetizeOutput
* `#1404 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1404>`_ - Autocompletion of cli does not work due to warning
* `#1408 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1408>`_ - GA fail for local platform
* `#1416 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1416>`_ - Default batch create_items method does not support kwargs
* `#1417 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1417>`_ - ITask To_Dict depends on platform_comps
* `#1436 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1436>`_ - Packages order is important in req2ac utility


CLI
---
* `#1430 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1430>`_ - Update yaspin requirement from ~=1.2.0 to ~=1.3.0


Dependencies
------------
* `#1340 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1340>`_ - Bump docker from 4.3.1 to 4.4.0
* `#1374 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1374>`_ - Update humanfriendly requirement from ~=8.2 to ~=9.0
* `#1387 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1387>`_ - Update coloredlogs requirement from ~=14.0 to ~=15.0
* `#1414 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1414>`_ - Update dramatiq[redis,watch] requirement from ~=1.9.0 to ~=1.10.0
* `#1418 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1418>`_ - Update docker requirement from <=4.4.0,>=4.3.1 to >=4.3.1,<4.5.0
* `#1435 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1435>`_ - Update gevent requirement from ~=20.12.1 to ~=21.1.2
* `#1442 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1442>`_ - Update pygit2 requirement from ~=1.4.0 to ~=1.5.0
* `#1444 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1444>`_ - Update pyyaml requirement from <5.4,>=5.3.0 to >=5.3.0,<5.5
* `#1448 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1448>`_ - Update matplotlib requirement from ~=3.3.3 to ~=3.3.4
* `#1449 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1449>`_ - Update jinja2 requirement from ~=2.11.2 to ~=2.11.3
* `#1450 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1450>`_ - Update sqlalchemy requirement from ~=1.3.22 to ~=1.3.23
* `#1457 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1457>`_ - Update more-itertools requirement from ~=8.6.0 to ~=8.7.0
* `#1466 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1466>`_ - Update tabulate requirement from ~=0.8.7 to ~=0.8.9
* `#1467 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1467>`_ - Update yaspin requirement from <1.4.0,>=1.2.0 to >=1.2.0,<1.5.0




Developer/Test
--------------
* `#1390 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1390>`_ - Update pytest requirement from ~=6.1.2 to ~=6.2.0
* `#1391 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1391>`_ - Update pytest-html requirement from ~=3.1.0 to ~=3.1.1
* `#1394 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1394>`_ - Update pytest-xdist requirement from ~=2.1 to ~=2.2
* `#1398 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1398>`_ - Update pytest requirement from ~=6.2.0 to ~=6.2.1
* `#1411 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1411>`_ - Update build tools to 1.0.3
* `#1413 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1413>`_ - Update idm-buildtools requirement from ~=1.0.1 to ~=1.0.3
* `#1424 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1424>`_ - Update twine requirement from ~=3.2.0 to ~=3.3.0
* `#1428 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1428>`_ - Update junitparser requirement from ~=1.6.3 to ~=2.0.0
* `#1434 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1434>`_ - Update pytest-cov requirement from ~=2.10.1 to ~=2.11.1
* `#1443 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1443>`_ - Update pytest requirement from ~=6.2.1 to ~=6.2.2
* `#1446 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1446>`_ - Update coverage requirement from ~=5.3 to ~=5.4
* `#1458 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1458>`_ - Update pytest-runner requirement from ~=5.2 to ~=5.3
* `#1463 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1463>`_ - Update allure-pytest requirement from ~=2.8.33 to ~=2.8.34
* `#1468 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1468>`_ - Update coverage requirement from <5.5,>=5.3 to >=5.3,<5.6
* `#1478 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1478>`_ - Update flake8 requirement from ~=3.8.4 to ~=3.9.0
* `#1481 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1481>`_ - Update twine requirement from ~=3.4.0 to ~=3.4.1




Documentation
-------------
* `#1259 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1259>`_ - Provide examples container and development guide
* `#1347 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1347>`_ - Read the Docs build broken, having issues with Artifactory/pip installation
* `#1423 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1423>`_ - Update sphinx-rtd-theme requirement from ~=0.5.0 to ~=0.5.1
* `#1474 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1474>`_ - Update sphinx requirement from ~=3.4.3 to ~=3.5.2


Feature Request
---------------
* `#1384 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1384>`_ - Add assets should ignore common directories through option
* `#1392 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1392>`_ - RequirementsToAssetCollection should allow to create user tag
* `#1437 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1437>`_ - req2ac utility should support getting compatible version (~=) of a package


Platforms
---------
* `#0558 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/558>`_ - Develop Test Harness for SSMT platform
