==============
Local platform
==============

To run simulations and experiments on the local platform you must have met the installation prerequisites. For more information, see :doc:`../installation`. In addition, the Docker client must be running. For more information, see |dev_install|.

Verify local platform is running
````````````````````````````````
Type the following at a command prompt to verify that local platform is running::

    idmtools local status

You should see the status of ``running`` for each of the following docker containers:

* idmtools_redis

* idmtools_postgres

* idmtools_workers

If not then you may need to run::

    idmtools local start

Run examples
````````````
To run the included examples on local platform you must configure :py:class:`~idmtools.core.platform_factory.Platform` to ``Local``, such as::

    platform = Platform('Local')

And, you must include the following block in the ``idmtools.ini`` file::

    [Local]
    type = Local

.. note::

    You should be able to use most of the included examples, see :doc:`../cli/cli-examples`, on local platform except for those that use :py:class:`~idmtools.entities.iworkflow_item.IWorkflowItem` or :py:class:`~idmtools.entities.suite.Suite` Python classes.

View simulations and experiments
````````````````````````````````
You can use the dashboard or the CLI for |IT_s| to view and monitor the status of your simulations and experiments.

The **dashboard** runs on a localhost server on port 5000 (http://localhost:5000). It is recommended that you use Google Chrome to open the dashboard.

The **CLI** command to see the status of simulations is::

    idmtools simulation --platform Local status

And, for experiments::

    idmtools experiment --platform Local status