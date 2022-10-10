===========
Development
===========


Additional Changes
------------------
* `#1671 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1671>`_ - experiment post creation hooks NOT get invoked


Bugs
----
* `#1581 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1581>`_ - We should default console=on for logging when use alias platform
* `#1614 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1614>`_ - User logger should only be used for verbose or higher messages
* `#1806 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1806>`_ - batch load module with wrong variable
* `#1807 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1807>`_ - get_children missing status refresh
* `#1811 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1811>`_ - Suite metadata not written when an experiment is run directly on slurm platform
* `#1812 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1812>`_ - Running a suite does not run containing children (experiments)
* `#1820 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1820>`_ - Handle empty status messages


CLI
---
* `#1774 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1774>`_ - need a patch release to update pandas requirement


Core
----
* `#1757 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1757>`_ - Suite to_dict method NO need to output experiments details


Dependencies
------------
* `#1749 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1749>`_ - Update pluggy requirement from ~=0.13.1 to ~=1.0.0
* `#1794 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1794>`_ - Bump pipreqs from 0.4.10 to 0.4.11
* `#1867 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1867>`_ - Update sqlalchemy requirement from ~=1.4.39 to ~=1.4.41
* `#1870 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1870>`_ - Update yaspin requirement from <2.2.0,>=1.2.0 to >=1.2.0,<2.3.0
* `#1873 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1873>`_ - Update docker requirement from <5.1.0,>=4.3.1 to >=4.3.1,<6.1.0
* `#1878 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1878>`_ - Update natsort requirement from ~=8.1.0 to ~=8.2.0
* `#1880 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1880>`_ - Update diskcache requirement from ~=5.2.1 to ~=5.4.0
* `#1882 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1882>`_ - Update flask requirement from ~=2.1.3 to ~=2.2.2
* `#1883 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1883>`_ - Update backoff requirement from <1.11,>=1.10.0 to >=1.10.0,<2.2
* `#1885 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1885>`_ - Bump async from 2.6.3 to 2.6.4 in /idmtools_platform_local/idmtools_webui

Developer/Test
--------------
* `#1795 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1795>`_ - Update twine requirement from ~=3.4.1 to ~=4.0.1
* `#1830 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1830>`_ - Update pytest requirement from ~=6.2.4 to ~=7.1.3
* `#1831 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1831>`_ - Update pytest-xdist requirement from ~=2.2 to ~=2.5
* `#1868 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1868>`_ - Update flake8 requirement from ~=4.0.1 to ~=5.0.4
* `#1874 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1874>`_ - Update allure-pytest requirement from <2.10,>=2.8.34 to >=2.8.34,<2.11
* `#1884 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1884>`_ - Update junitparser requirement from ~=2.1.1 to ~=2.8.0

Feature Request
---------------
* `#1691 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1691>`_ - Feature request: Add existing experiments to suite
* `#1809 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1809>`_ - Add cpus_per_task to SlurmPlatform
* `#1818 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1818>`_ - Improve the output to user after a job is executed
* `#1821 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1821>`_ - Status improvement: make "checking slurm finish" configurable


Platforms
---------
* `#1678 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1678>`_ - Retry logic for slurm
* `#1717 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1717>`_ - Formalize shell script for SLURM job submission
* `#1758 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1758>`_ - Document how to cancel jobs on slurm using slurm docs
* `#1764 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1764>`_ - Update the sbatch script to dump the SARRAY job id
* `#1765 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1765>`_ - Update the simulation script to dump the Job id into a file within each simulation directory
* `#1770 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1770>`_ - Develop base singularity image
* `#1822 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1822>`_ - COMPSPlatform suite operation: platform_create returns Tuple[COMPSSuite, UUID]
