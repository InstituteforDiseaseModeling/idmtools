======================
Create simulation tags
======================

During the creation of simulations you can add tags, key:value pairs, included as metadata. The tags can be used for filtering on and searching for simulations. |IT_s| includes multiple ways for adding tags to simulations:

* (Preferred) Builder callbacks with :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` or :py:class:`~idmtools.entities.simulation.Simulation`
* Base task with :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations`
* Specific simulation from :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations`

(Preferred) Builder callbacks via add_sweep_definition
======================================================
You can add tags to simulations by using builder callbacks while building experiments with :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` or :py:class:`~idmtools.entities.simulation.Simulation` classes and the **add_sweep_definition** method. This way supports adding tags to a large set of simulations and gives you full control over the simulation/task object. In addition, built-in tag management support is used when implementing the return values in a dictionary for the tags. For more information see the example in :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder`.

Base task with TemplatedSimulations
===================================
You can add tags to all simulations via base task used with the
:py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations` class while building simulations. For more information see the example in :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations`.

Specific simulation from TemplatedSimulations
=============================================
If you need to add a tag to a specific simulation after building simulations from task with :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations`, then you must convert the simulations to a list. For more information see the example in :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations`.
