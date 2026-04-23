# Changelog

All notable changes to idmtools will be documented here.

---
## [3.1.0]

### Feature Requests

- [#2727](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2727) - Change codebase and release packages from Jfrog to Pypi
- [#2648](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2648) - Doc Update: Re-write/update idmtools document (MkDocs)
- [#2711](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2711) - Explicitly define parameters for add_schedule_config and default_add_schedule_config_sweep_callback in comps scheduling
- [#2710](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2710) - GHA toc-generator.yml update
- [#2716](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2716) - Remove bump2version code and package
- [#2713](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2713) - Remove no needed function platform_task_hooks and file python_version.py

### Bug Fixes

- [#2693](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2693) - Platform(docker_image=<image>) does not check if the docker_image has been updated
- [#2712](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2712) - Bug: can not build singularity from GHCR docker image
- [#2709](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2709) - task.to_simulation missing name input
- [#2717](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2717) - Fix python command issue for all platforms
- [#2723](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2723) - Bug: when a running container is found, the code reuses it without checking if it was started from the current image version
- [#2632](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2632) - Simulation.from_task(task) missing name input
- [#2633](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2633) - COMPSPlatform:  batch_create didn't pass kwargs to batch_create_items

### Configuration

- [#2639](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2639) - Remove legacy DTKTools ini file parameters (max_threads, sims_per_thread, max_local_sims)

### Documentation

- [#2714](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2714) - Fix all README.md file
- [#2715](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2715) - Add Github Actions script to deploy mkdoc document

### Developer/Test

- [#2718](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2718) - Cleanup Makefiles and devscripts
- [#2719](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2719) - Integration test with new emod ubuntu runtime docker image
- [#2720](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2720) - Build singularity image in COMPS from ubuntu docker image

### Other

- [#2649](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2649) - Sync/Update idmtools-calibra
---

## [3.0.0]

### Feature Requests

- [#2423](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2423) - Remove Suite from Suite/Experiment/Simulation structure
- [#2550](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2550) - Remove add_dummy_suite by default for file/container/slurm platforms
- [#2545](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2545) - Container Platform should not make root as default user
- [#2564](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2564) - Enhance get_directory, possibly using caching to cut build time
- [#2565](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2565) - Make wait refresh_interval configurable
- [#2572](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2572) - Add tags.json file for simulation/experiment/suite folder
- [#2578](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2578) - Better to clear up the entity's _platform_directory cache before run entity

### Bug Fixes

- [#2553](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2553) - User should not need to call platform.create_item themself
- [#2554](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2554) - Access exp.parent may throw exception
- [#2555](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2555) - Access sim.parent may throw exception
- [#2556](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2556) - experiment.add_simulation(sim) didn't set sim.parent for newly added sim
- [#2558](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2558) - Simulation has no experiment_id field, just inherits parent_id
- [#2559](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2559) - Suite retrieved from cache (or pickle) has experiments is None
- [#2561](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2561) - Experiment.simulations.append may add duplicate simulation
- [#2577](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2577) - Make behaviors consistent when calling get_directory
- [#2580](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2580) - Container platform sims sometimes fail to create

### Developer/Test

- [#2567](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2567) - Fully idmtools testing for all changes (major Suite structure changes)
- [#2589](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2589) - Update docs with new folder structure changes

---

## [2.2.0]

### Bug Fixes

- [#2478](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2478) - bootstrap.py didn't initialize logging well
- [#2207](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2207) - Fix AnalyzeManager: output message
- [#2502](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2502) - AnalyzeManager not able to retrieve assets files
- [#2503](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2503) - get_files failed with COMPS Simulation

### Core

- [#2469](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2469) - Remove sequence id utility
- [#2473](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2473) - Update plugin and alias

### Developer/Test

- [#2472](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2472) - Test calibration with new changes
- [#2474](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2474) - Update dev scripts
- [#2476](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2476) - Update unit tests
- [#2484](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2484) - Remove slurm utils GA related scripts
- [#2490](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2490) - Test AnalyzeManager and PlatformAnalysis

### Documentation

- [#2475](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2475) - Update idmtools documents
- [#2535](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2535) - Intermittent Sphinx Build Failures Triggered by PUML Rendering

### Feature Requests

- [#2493](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2493) - Epic: Add tag-based filtering and other utility enhancements
- [#2494](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2494) - Reallocate JobHistory utility and we may use it in other platforms
- [#2498](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2498) - Add get_directory methods for Suite/Experiment/Simulations
- [#2499](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2499) - Add get_simulations() and get_experiments()
- [#2500](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2500) - Add simulation filtering with tags
- [#2504](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2504) - get_files is case-sensitive on file names
- [#2510](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2510) - Reduce UI tags space used by idmtools task_type tag in Simulation/Experiment

### Platforms

- [#2424](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2424) - Epic: Refactor SLURMPlatform to reduce the duplicate coding
- [#2465](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2465) - Update tests and GHA for SLURM platform change
- [#2466](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2466) - Make SlurmPlatform inherit from FilePlatform
- [#2467](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2467) - Refactor FilePlatform
- [#2468](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2468) - Remove bridged and remote utility
- [#2483](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2483) - Remove mode related functions
- [#2488](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2488) - Consolidate FileExperiment, SlurmExperiment, etc.
- [#2489](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2489) - Refactor flatten_item method

### Other

- [#2477](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2477) - Refactor Slurm Platform: prepare new idmtools 2.2.0 release
- [#2491](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2491) - Work with EMOD team to test before the release

### Support

- [#2482](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2482) - bootstrap.py may encounter "Access is denied." issue

---

## [2.1.0]

### Bug Fixes

- [#2420](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2420) - Fix Macbook issues to support ContainerPlatform
- [#2413](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2413) - CommandLine.add_option adds extra double quotes around strings with spaces, making file paths inaccessible
- [#2422](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2422) - Not providing the appropriate message while running container platform on Windows when Developer Mode is off
- [#2432](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2432) - idmtools_platform_comps/ssmt_work_items/work_order.py field error cause doc build fail
- [#2426](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2426) - Arm simulation builder does not throw an appropriate error message if configured wrong

### Documentation

- [#2431](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2431) - Fix document build issue with idm-buildtools

### Feature Requests

- [#2445](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2445) - Fix pip install issue which depends on index-url or extra-index-url
- [#2450](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2450) - Create devcontainer for CodeSpaces

### Platforms

- [#2421](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2421) - Run script as a SLURM job
- [#1574](https://github.com/InstituteforDiseaseModeling/idmtools/issues/1574) - Can not download AssetCollection files with platform.get_files_by_id

### User Experience

- [#2415](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2415) - Write doc to summarize ContainerPlatform support on Macbook

---

## [2.0.2]

### Bug Fixes

- [#2391](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2391) - Random fail with large number of simulations with NoneType of platform
- [#2393](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2393) - Calibra may fail with ContainerPlatform
- [#2395](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2395) - Slurm: Do not need to delete suite if job_directory is not exist or suite not exist anymore
- [#2399](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2399) - docker container can become unusable in linux

### Documentation

- [#2386](https://github.com/InstituteforDiseaseModeling/idmtools/pull/2386) - jupyter lab version fix

### Feature Requests

- [#2377](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2377) - Need to change github actions to only build container docker image when there are related changes
- [#2172](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2172) - Adjust the default 'max_running_jobs' in SlurmPlatform
- [#2379](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2379) - Container Platform needs to support multiple processes
- [#2396](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2396) - Assets duplication

### Platforms

- [#2388](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2388) - Performance issue with get_item in slurm platform when there are lot of items in job directory
- [#2389](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2389) - Performance issue with get_item in container platform when there are lot of items in job directory
- [#2247](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2247) - Investigation: run each simulation on SLURM with multi cores

### Release/Packaging

- [#2400](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2400) - Add script for generating changelog by project id and release version

### User Experience

- [#2387](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2387) - Investigation multiple warnings for binding in NU cluster for singularity
- [#2145](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2145) - slurm platform -- unable to run from compute nodes as expected

---

## [2.0.1]

### Bug Fixes

- [#2380](https://github.com/InstituteforDiseaseModeling/idmtools/issues/2380) - Needs to put Nibbler to linux_mounts.py

---

For older changelogs, see the [GitHub releases page](https://github.com/InstituteforDiseaseModeling/idmtools/releases).
