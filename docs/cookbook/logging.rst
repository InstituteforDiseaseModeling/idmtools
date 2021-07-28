=======
Logging
=======

Enabling/Disabling/Changing Log Level at Runtime
------------------------------------------------

Sometime you want to be able to enable console logging or change a logging level directly in a script without the need for an idmtools.ini file. The following example shows how to do that.

.. literalinclude:: ../../examples/cookbook/logging/enable_at_run_time.py
    :language: python

See :ref:`Logging Overview` for details on configuring logging through the *idmtools.ini*.