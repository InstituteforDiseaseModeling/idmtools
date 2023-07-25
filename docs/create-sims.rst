==========================
Create and run simulations
==========================

To create simulations with |IT_s|, create a Python file that imports the relevant packages, uses the classes and functions to meet your specific needs, and then run the script using ``python script_name.py``.

For example, if you would like to create many simulations "on-the-fly" (such as parameter sweeps) then you should use the :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` and :py:class:`~idmtools.entities.templated_simulation.TemplatedSimulations` classes. On the other hand, if you would like to create multiple simulations beforehand then you can use the :py:class:`~idmtools.entities.simulation.Simulation` class.


See the following examples for each of these scenarios:

SimulationBuilder example
-------------------------

.. literalinclude:: ../examples/builders/experiment_builder_python.py
    :language: python

Simulation example
------------------

.. literalinclude:: ../examples/builders/manual_building.py
    :language: python

Many additional examples can be found in the `/examples`_ folder of the GitHub repository.

.. _/examples: https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/examples

.. toctree::

    create-sims-tags
    create-sims-emod
