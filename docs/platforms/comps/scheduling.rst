.. _COMPS_Scheduling:

Scheduling
==========

Idmtools supports job scheduling on the |COMPS_s| platform, which includes support for multiple scenarios depending upon the scheduling needs of your specific research needs and requirements. For example, you could schedule your simulations to run under a single process on the same node and with a specified number of cores. For more information about this and other supported scenarios, see `Scenarios`_. To use the full scheduling capabilites included within |COMPS_s| you must add the scheduling information to a ``workorder.json`` file, to include as part of the asset collection. This is a one time task to complete for your project. For more information about scheduling configuration, see `Configuration`_. `Examples`_ are provided from which you can leverage to help get started and gain a better understanding.


.. _Scenarios:

Scenarios
---------

Choosing the correct scheduling scenario will depend upon your specific research needs and requirements. The following lists some of the common scenarios supported: 

* N cores, N processes - useful for single-threaded or MPI-enabled workloads, such as |EMOD_s|.
* N cores, 1 node, 1 process - useful for models that want to spawn various worker thread (GenEpi) or have large memory usage, where the number of cores being an indicator of memory usage.
* 1 node, N processes - useful for models with high migration and interprocess communication. By running on the same node MPI can use shared memory, as opposed to slower tcp sockets over multiple nodes. This may be useful for some scenarios using |EMOD_s| or other MPI-enabled workloads.


.. _Configuration:

Configuration
-------------

By configuring a ``workorder.json`` file and including it in your asset collection you can take advantage of the full scheduling support provided with |COMPS_s|. Scheduling information included in the workorder.json file will take precedent over any scheduling information you may have in the idmtools.ini file or scheduling parameters passed to a work item. The following example shows some of the options available to include in a workorder.json file::

    {
      "Command": "python3 Assets/model1.py",
      "NodeGroupName": "idm_abcd",
      "NumCores": 1,
      "NumProcesses": 1,
      "NumNodes": 1,
      "Environment": {
        "key1": "value1",
        "key2:": "value2",
        "PYTHONPATH": "$PYTHONPATH:$PWD/Assets:$PWD/Assets/site-packages",
        "PATH": "$PATH:$PWD/Assets:$PWD/Assets/site-packages"
      }
    }

As illustrated in the above example of including common scheduling items like cores, processess, and nodes, you can also specify dynamic environment variables, such as PYTONPATH and PATH, to be set at run time.

In addition to including a workorder.json file you must also set and pass ``scheduling=True`` parameter when running simulations, for example::

    experiment.run(scheduling=True)

.. _Examples:

Example
-------

For addition information and specifics of using a workorder.json file within Python, you can begin with the following:

.. literalinclude:: ../../../examples/python_model/python_sim_scheduling.py
    :language: python
