==================
Create simulations
==================

There are different ways to create simulations with |IT_s|. Depending upon your objective will help determine which simulation class objects to use. For example, if you would like to create many simulations "on-the-fly" (such as parameter sweeps) then you should use the :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` and :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations` classes. On the other hand, if you would like to create multiple simulations beforehand then you can use the :py:class:`~idmtools.entities.simulation.Simulation` class. See the following examples for each of these scenarios:

SimulationBuilder example
-------------------------

.. literalinclude:: ../examples/builders/experiment_builder_python.py
    :language: python

Simulation example
------------------

.. literalinclude:: ../examples/builders/manual_building.py
    :language: python

.. toctree::

    create-sims-tags
    create-sims-emod