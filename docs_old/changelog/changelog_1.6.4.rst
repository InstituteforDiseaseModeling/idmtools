=====
1.6.4
=====


Additional Changes
------------------
* `#1407 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1407>`_ - import get_latest_package_version_from_pypi throws exception
* `#1593 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1593>`_ - Pandas items as defaults cause issue with Simulation Builder


Analyzers
---------
* `#1097 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1097>`_ - Analyzer may get stuck on error
* `#1506 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1506>`_ - DownloadAnalyzer should not stop if one sim fails, but try to download all sims independently.
* `#1540 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1540>`_ - Convert AnalyzeManager to use futures and future pool
* `#1594 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1594>`_ - Disable log re-initialization in subthreads
* `#1596 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1596>`_ - PlatformAnalysis should support extra_args to be passed to AnalyzeManager on the server
* `#1608 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1608>`_ - CSVAnalyzer should not allow users to override parse value as it is required


Bugs
----
* `#1452 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1452>`_ - idmtools work for using new slurm scheduling mechanism 
* `#1518 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1518>`_ - CommandLine add_argument should convert arguments to strings
* `#1522 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1522>`_ - Load command line from work order on load when defined



Core
----
* `#1586 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1586>`_ - Fix the help on the top-level makefile


Dependencies
------------
* `#1440 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1440>`_ - Update diskcache requirement from ~=5.1.0 to ~=5.2.1
* `#1490 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1490>`_ - Update flask-sqlalchemy requirement from ~=2.4.4 to ~=2.5.1
* `#1498 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1498>`_ - Update yaspin requirement from <1.5.0,>=1.2.0 to >=1.2.0,<1.6.0
* `#1520 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1520>`_ - Update docker requirement from <4.5.0,>=4.3.1 to >=4.3.1,<5.1.0
* `#1545 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1545>`_ - Update pygithub requirement from ~=1.54 to ~=1.55
* `#1552 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1552>`_ - Update matplotlib requirement from ~=3.4.1 to ~=3.4.2
* `#1555 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1555>`_ - Update sqlalchemy requirement from ~=1.4.14 to ~=1.4.15
* `#1562 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1562>`_ - Bump werkzeug from 1.0.1 to 2.0.1
* `#1563 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1563>`_ - Update jinja2 requirement from ~=2.11.3 to ~=3.0.1
* `#1566 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1566>`_ - Update cookiecutter requirement from ~=1.7.2 to ~=1.7.3
* `#1568 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1568>`_ - Update more-itertools requirement from ~=8.7.0 to ~=8.8.0
* `#1570 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1570>`_ - Update dramatiq[redis,watch] requirement from ~=1.10.0 to ~=1.11.0
* `#1585 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1585>`_ - Update psycopg2-binary requirement from ~=2.8.6 to ~=2.9.1


Developer/Test
--------------
* `#1511 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1511>`_ - Add document linting to rules
* `#1549 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1549>`_ - Update pytest requirement from ~=6.2.3 to ~=6.2.4
* `#1554 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1554>`_ - Update flake8 requirement from ~=3.9.1 to ~=3.9.2
* `#1567 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1567>`_ - Update allure-pytest requirement from <2.9,>=2.8.34 to >=2.8.34,<2.10
* `#1577 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1577>`_ - Update junitparser requirement from ~=2.0.0 to ~=2.1.1
* `#1587 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1587>`_ - update docker python version


Documentation
-------------
* `#0944 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/944>`_ - Set up intersphinx to link emodpy and idmtools docs
* `#1445 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1445>`_ - Enable intersphinx for idmtools
* `#1499 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1499>`_ - Update sphinx requirement from ~=3.5.2 to ~=3.5.3
* `#1510 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1510>`_ - Update sphinxcontrib-programoutput requirement from ~=0.16 to ~=0.17
* `#1516 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1516>`_ - Update sphinx-rtd-theme requirement from ~=0.5.1 to ~=0.5.2
* `#1531 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1531>`_ - Update sphinx requirement from ~=3.5.3 to ~=3.5.4
* `#1584 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1584>`_ - Update sphinx-copybutton requirement from ~=0.3.1 to ~=0.4.0


Feature Request
---------------
* `#0831 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/831>`_ - Support for python 3.9


Platforms
---------
* `#1604 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1604>`_ - idmtools_platform_local run "make docker" failed


User Experience
---------------
* `#1485 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1485>`_ - Add files and libraries to an Asset Collection - new documentation
