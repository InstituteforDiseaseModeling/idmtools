===========
Environment
===========

Modifying environment variables on platforms without native support
-------------------------------------------------------------------

Some platforms do not support changing environment variables in a job
definition. |IT_s| provides a utility through
:py:class:`~idmtools_models.templated_script_task.TemplatedScriptTask`
to allow you to still modify environment variables, as demonstrated in the
following example.

Here is our model.py. It imports our package and then prints the environment
variable "EXAMPLE".

.. literalinclude:: ../../examples/cookbook/environment/variables/model.py
    :language: python

This is our |IT_s| orchestration script that defines our Python task and wrapper
task with additional variables.

.. literalinclude:: ../../examples/cookbook/environment/variables/environment-vars.py
    :language: python