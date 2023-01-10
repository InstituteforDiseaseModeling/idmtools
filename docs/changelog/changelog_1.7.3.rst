
=====
1.7.3
=====
    

Additional Changes
------------------
* `#1835 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1835>`_ - Do the release of 1.7.0.pre
* `#1837 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1837>`_ - Release 1.7.0
* `#1855 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1855>`_ - Generate Changelog for 1.7.0
* `#1857 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1857>`_ - Test final singularity image
* `#1858 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1858>`_ - Complete basic use of idmtools-slurm-bridge docs
* `#1863 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1863>`_ - Presentation for Jaline
* `#1876 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1876>`_ - Build new singularity image


Bugs
----
* `#1623 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1623>`_ - We should not generate debug log for _detect_command_line_from_simulation in simulation_operations.py
* `#1661 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1661>`_ - Script seems to require pwd module but not included in requirements.txt
* `#1666 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1666>`_ - logging.set_file_logging should pass level to create_file_handler()
* `#1756 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1756>`_ - Suite Operation run_item doesn't pass kwargs to sub-calls
* `#1813 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1813>`_ - Writing experiment parent id in experiment metadata records the wrong suite id
* `#1877 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1877>`_ - Revert sphinx to 4 and pin in dependabot
* `#1907 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1907>`_ - Make cache directory configurable
* `#1915 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1915>`_ - run_simulation.sh should be copied over instead of link


Core
----
* `#1826 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1826>`_ - Update to require at east python 3.7


Dependencies
------------
* `#1906 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1906>`_ - Update pygithub requirement from ~=1.55 to ~=1.56
* `#1910 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1910>`_ - Update flask-sqlalchemy requirement from ~=2.5.1 to ~=3.0.2
* `#1911 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1911>`_ - Update sqlalchemy requirement from ~=1.4.41 to ~=1.4.42
* `#1912 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1912>`_ - Update gevent requirement from <21.13.0,>=20.12.1 to >=20.12.1,<22.11.0
* `#1914 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1914>`_ - Update more-itertools requirement from ~=8.14.0 to ~=9.0.0
* `#1920 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1920>`_ - Update psycopg2-binary requirement from ~=2.9.4 to ~=2.9.5
* `#1921 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1921>`_ - Update pytest-html requirement from ~=3.1.1 to ~=3.2.0
* `#1922 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1922>`_ - Update pycomps requirement from ~=2.8 to ~=2.9
* `#1923 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1923>`_ - Update colorama requirement from ~=0.4.5 to ~=0.4.6
* `#1933 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1933>`_ - Update pytest-xdist requirement from ~=2.5 to ~=3.0
* `#1934 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1934>`_ - Update pytest requirement from ~=7.1.3 to ~=7.2.0
* `#1942 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1942>`_ - Update sqlalchemy requirement from ~=1.4.42 to ~=1.4.43
* `#1943 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1943>`_ - Update pygithub requirement from ~=1.56 to ~=1.57


Developer/Test
--------------
* `#1649 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1649>`_ - github action test failed which can not retrieve the latest ssmt image
* `#1652 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1652>`_ - Changelog not showing after 1.6.2 release


Documentation
-------------
* `#1378 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1378>`_ - Container Python Package development guide
* `#1453 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1453>`_ - emodpy example for the local platform


Feature Request
---------------
* `#1359 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1359>`_ - PlatformFactory should save extra args to an object to be able to be serialized later


Platforms
---------
* `#1853 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1853>`_ - Add utils to platform-comps Utils
* `#1854 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1854>`_ - Add utils to platform-slurm utils
* `#1864 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1864>`_ - Document user installed packages in Singularity images


User Experience
---------------
* `#1804 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1804>`_ - Default root for run/job directories in slurm local platform is '.'
* `#1805 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/1805>`_ - Slurm local platform should make containing experiments/suites as needed
