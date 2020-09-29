==========================
Environment
==========================

Modifying environment variables on platforms without native support
-------------------------------------------------------------------

Some platforms do not support changing environment variables in a job definition. IDMTools provides a utility through the TemplatedTaskWrapperTask to allow you to still modify environment variables. In the below example, we use that utility to run

Here is our model.py. It imports our package and then prints the environment variable "EXAMPLE"

.. literalinclude:: ../examples/cookbook/environment/variables/model.py
    :language: python

This is our idmtools orchestration script to run the defines our python task and wrapper task with additional variables

.. literalinclude:: ../examples/cookbook/environment/variables/environment-vars.py
    :language: python