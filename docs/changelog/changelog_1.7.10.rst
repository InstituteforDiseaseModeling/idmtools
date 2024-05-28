
======
1.7.10
======
    

Bugs
----
* `#2158 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2158>`_ - Fix pygit2
* `#2165 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2165>`_ - ArmSimulationBuilder display simulation count incorrect
* `#2216 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2216>`_ - pywin32 package did not install with windows platform for idmtools_test
* `#2217 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2217>`_ - simulation_build throw error with python3.7
* `#2218 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2218>`_ - fileplatform can not create simlink with windows and python <3.8
* `#2232 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2232>`_ - Fix and improve platform_task_hooks


CLI
---
* `#2174 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2174>`_ - Update and move unittests in core and cli packages not depending on idmtools_models package


Core
----
* `#2183 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2183>`_ - SimulationBuilder assume input values object has __len__ defined
* `#2166 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2166>`_ - SweepArm should support add_multiple_parameter_sweep_definition
* `#2167 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2167>`_ - ArmSimulationBuilder needs rasie exception for call to add_sweep_definition and add_multiple_parameter_sweep_definition
* `#2168 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2168>`_ - Refactor ArmSimulationBuilder and move general functionality to a base class
* `#2184 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2184>`_ - Improved Simulation builders (fixed several issues)
* `#2192 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2192>`_ - Builder function add_multiple_parameter_sweep_definition doesn't support function with single dictionary parameter
* `#2194 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2194>`_ - Sweeping function allow parameters with default values
* `#2195 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2195>`_ - Combine two add sweeping functions into one
* `#2196 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2196>`_ - Refactor Simulation Builders to remove duplicated code
* `#2214 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2214>`_ - Investigation: idmtools support Python 3.12
* `#2203 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2203>`_ - Refactor idmtools Simulation Builders structure.
* `#2206 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2206>`_ - Investigate pkg_resources package replacement which was removed from Python 3.12


Dependencies
------------
* `#2176 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2176>`_ - Update jinja2 requirement from ~=3.1.2 to ~=3.1.3
* `#2180 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2180>`_ - Update click requirement from ~=8.1.3 to ~=8.1.7
* `#2181 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2181>`_ - Update packaging requirement from <22.0,>=20.4 to >=20.4,<24.0
* `#2182 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2182>`_ - Update readthedocs-sphinx-search requirement from ~=0.3.1 to ~=0.3.2
* `#2189 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2189>`_ - Update yaspin requirement from <2.4.0,>=1.2.0 to >=1.2.0,<3.1.0
* `#2199 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2199>`_ - Update cookiecutter requirement from ~=2.1.1 to ~=2.6.0
* `#2204 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2204>`_ - Update pytest-timeout requirement from ~=2.1.0 to ~=2.3.1
* `#2212 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2212>`_ - Update jupyterlab requirement from ~=4.0.2 to ~=4.1.5
* `#2220 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2220>`_ - Update pluggy requirement from ~=1.2 to ~=1.4
* `#2221 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2221>`_ - Update nbsphinx requirement from ~=0.9.2 to ~=0.9.3
* `#2222 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2222>`_ - Update packaging requirement from ~=23.2 to ~=24.0
* `#2223 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2223>`_ - Update pygithub requirement from ~=1.57 to ~=2.3
* `#2227 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2227>`_ - Update idm-buildtools requirement from ~=1.0.3 to ~=1.0.5
* `#2228 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2228>`_ - Update junitparser requirement from ~=3.1.1 to ~=3.1.2
* `#2229 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2229>`_ - Update coverage requirement from <6.6,>=5.3 to >=5.3,<7.5
* `#2230 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2230>`_ - Update flake8 requirement from ~=6.0.0 to ~=7.0.0
* `#2231 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2231>`_ - Update pytest-xdist requirement from ~=3.3 to ~=3.5


Developer/Test
--------------
* `#2155 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2155>`_ - Remove Bayesian tests
* `#2175 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2175>`_ - Fix circular dependency for core and cli tests and move comps related test in core to comps test
* `#2213 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2213>`_ - Fix bug for save_as for content type and add unittest
* `#2226 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2226>`_ - unregister plugin in test_hooks.py to avoid affecting other test


Feature Request
---------------
* `#2032 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2032>`_ - Assetization workflow for generating SIF image should track using Asset ID instead of AC ID
* `#2160 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2160>`_ - Remove local platform from idmtools repo
* `#2170 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2170>`_ - Move unit tests in core package which depend on idmtools_platform_comps to idmtools_platform_comps
* `#2210 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2210>`_ - Add download asset and use asset id in generate singularity builder instead of assetcollection
* `#2215 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2215>`_ - Update idmtools to work with python 3.12


Platforms
---------
* `#2164 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2164>`_ - Update tests from windows(Cumulus) to SlurmStage
* `#2173 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2173>`_ - Give deprecating warning for duplicate wait_on_done function
* `#2224 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2224>`_ - Migrate all examples and tests which reference Belegost or Bayesian to Caculon


User Experience
---------------
* `#2233 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2233>`_ - Consider un-register idmtools plugin
