==========================
Python
==========================

Adding items to the Python Path
----------------------------------

The example below runs a simple model that depends on a user produced package. It uses a wrapper script to add the items
the PYTHONPATH environment variables so the package can easily be imported into our model.py

Here is our dummy package. It just has a variable we are going to use in model.py

.. literalinclude:: ../../examples/cookbook/python/python-path/a_package.py
    :language: python

Here is our model.py. It imports our package and then prints the variables defined in our model

.. literalinclude:: ../../examples/cookbook/python/python-path/model.py
    :language: python

This is our idmtools orchestration script to run the add our package, define our python task, and wrap that with a bash script.

.. literalinclude:: ../../examples/cookbook/python/python-path/python-path.py
    :language: python
