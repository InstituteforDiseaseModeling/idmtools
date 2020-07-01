==============
Local platform
==============

To run simulations and experiments on the local platform you must have met the installation prerequisites. For more information, see :doc:`installation`. In addition, the Docker client must be running. For more information, see :ref:`Start the Docker client` section in :doc:`dev-installation`.

Verify local platform is running
````````````````````````````````
Type the following at a command prompt to verify that local platform is running::

    idmtools local status

You should see the status of ``running`` for each of the following docker containers:

* idmtools_redis

* idmtools_postres

* idmtools_workers

If not then you may need to run::

    idmtools local start

Run examples
````````````
To run the included examples on local platform you must configure the :py:class:`~idmtools.core.platform_factory.Platform` to ``Local``, such as::

    platform = Platform('Local')

And, you must include the following block in the ``idmtools.ini`` file::

    [Local]
    type = Local

.. note::

    You should be able to use most of the included examples, see :doc:`cli-examples`, on local platform except for those that use :py:class:`~idmtools.entities.iworkflow_item.IWorkflowItem` or :py:class:`~idmtools.entities.suite.Suite` Python classes.

View simulations and experiments
````````````````````````````````
You can view the status of your simulations and experiments by opening up the |IT_s| dashboard, which runs on a localhost server on port 5000 (http://localhost:5000). It is recommended that you use Google Chrome to open the dashboard.
