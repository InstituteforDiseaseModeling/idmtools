========
Builders
========

Simulation Builder
------------------

The follow demonstrates how to build a sweep using the standard builder, :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder`

This example uses the following model.

.. literalinclude:: ../../idmtools_test/idmtools_test/inputs/python/model1.py
    :language: python

It then builds sweeps through *Arms*

.. literalinclude:: ../../examples/builders/simulation_builder.py
    :language: python

See :py:class:`~idmtools.builders.simulation_builder.SimulationBuilder` for more details.


Arm Experiment Builder
----------------------

The follow demonstrates how to build a sweep using :py:class:`~idmtools.builders.arm_simulation_builder.ArmSimulationBuilder`

This example uses the following model.

.. literalinclude:: ../../idmtools_test/idmtools_test/inputs/python/model1.py
    :language: python

It then builds sweeps through *Arms*

.. literalinclude:: ../../examples/builders/arm_experiment_builder_python.py
    :language: python

See :py:class:`~idmtools.builders.arm_simulation_builder.ArmSimulationBuilder` for more details

Multiple argument sweep
-----------------------

The follow demonstrates how to build a sweep when multiple arguments are required at the
same time. Typically, defining sweeps per argument is best like in the example :ref:`Simulation Builder`
but in some cases, such as when we need all parameters to create an object, we want these parameters passed to a single callback at the same time. This example uses the following model.

.. literalinclude:: ../../idmtools_test/idmtools_test/inputs/python/model1.py
    :language: python

We then make a class within our example script that requires the parameters *a*, *b*, and *c* be defined at creation time. With this defined, we then add our sweep callback.

.. literalinclude:: ../../examples/builders/multi_argument_sweep.py
    :language: python
