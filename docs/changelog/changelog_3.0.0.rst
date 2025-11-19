.. _changelog-3.0.0:


=====
3.0.0
=====

Feature Request
---------------
* `#2423 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2423>`_ - Remove Suite from Suite/Experiment/Simulation structure
* `#2550 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2550>`_ - Remove add_dummy_suite by default for file/container/slurm platforms
* `#2545 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2545>`_ - Container Platform should not make root as default user
* `#2564 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2564>`_ - Enhance get_directory, possibly using caching to cut build time.
* `#2565 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2565>`_ - Make wait refresh_interval configurable.
* `#2572 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2572>`_ - Add tags.json file for simulation/experiment/suite folder
* `#2578 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2578>`_ - Better to clear up the entity's _platform_directory cache before run entity.

Bugs
----
* `#2553 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2553>`_ - User should not need to call platform.create_item themself
* `#2554 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2554>`_ - Access exp.parent may throw exception
* `#2555 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2555>`_ - Access sim.parent may throw exception
* `#2556 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2556>`_ - experiment.add_simulation(sim) didn't set sim.parent for newly added sim
* `#2558 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2558>`_ - Simulation has no experiment_id field, just inherits parent_id
* `#2559 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2559>`_ - Suite retrieved from cache (or pickle) has experiments is None
* `#2561 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2561>`_ - Experiment.simulations.append may add duplicate simulation
* `#2577 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2577>`_ - Make behaviors consistent when calling get_directory
* `#2580 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2580>`_ - Container platform sims sometimes fail to create

Developer/Test
--------------
* `#2567 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2567>`_ - Fully idmtools testing for all changes (major Suite structure changes)
* `#2589 <https://github.com/InstituteforDiseaseModeling/idmtools/issues/2589>`_ - Update docs with new folder structure changes
