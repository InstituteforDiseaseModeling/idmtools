===========
Experiments
===========

Adding simulations to an existing experiment
--------------------------------------------

.. literalinclude:: ../../examples/cookbook/experiments/add_simulation_to_existing_experiment.py
    :language: python

Adding simulations to an existing experiment with new common assets
-------------------------------------------------------------------

.. literalinclude:: ../../examples/cookbook/experiments/add_simulation_to_existing_experiment_with_new_assets.py
    :language: python

Creating experiments with one simulation
----------------------------------------

When you want to run a single simulation instead of a set, you can create an experiment directly
from a task.

.. literalinclude:: ../../examples/cookbook/experiments/create_experiment_with_one_sim.py
    :language: python

Creating an experiment with a pre- and post- creation hook
----------------------------------------------------------

Prior to running an experiment or a work item, you can add pre or post creation hooks to the item.

.. literalinclude:: ../../examples/cookbook/experiments/create_experiment_with_hooks.py
    :language: python