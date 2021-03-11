.. _COMPS_Scheduling:

Scheduling
==========

Idmtools supports job scheduling on the |COMPS_s| platform, which includes support for multiple scenarios depending upon the scheduling needs of your specific research needs and requirements. For example, you could schedule your simulations to run under a single process on the same node and with a specified number of cores. For more information about this and other supported scenarios, see `Scenarios`_. To use the full scheduling capabilites included within |COMPS_s| you must add the ``workorder.json`` as a transient asset. This is a one time task to complete for your project. For more information about scheduling configuration, see `Configuration`_. `Examples`_ are provided from which you can leverage to help get started and gain a better understanding. `Schemas`_ enumerate the available options that may be included in workorder.json.


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

By configuring a ``workorder.json`` file and adding it as a transient asset you can take advantage of the full scheduling support provided with |COMPS_s|. Scheduling information included in the workorder.json file will take precedent over any scheduling information you may have in the idmtools.ini file or scheduling parameters passed to a work item. The following examples shows some of the options available to include in a workorder.json file. To see the list of alias' for the clusters on |COMPS_s|, use the following CLI command: ``idmtools info plugins platform-aliases``.

**Example workorder.json for HPC clusters**::

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

**Example workorder.json for SLURM clusters**::

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

In addition to including a workorder.json file you must also set and pass ``scheduling=True`` parameter when running simulations, for example::

    experiment.run(scheduling=True)

Add workorder.json as a transient asset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To include the workorder.json file as a transient asset you can either add an existing workorder.json using the ``add_work_order`` method or dynamically create one using the ``add_schedule_config`` method, both methods included in the :py:class:`~idmtools.idmtools_platform_comps.utils.Scheduling` class.

**Add existing workorder.json**::

    add_work_order(ts, file_path=os.path.join(COMMON_INPUT_PATH, "scheduling", "slurm", "WorkOrder.json"))

**Dynamically create workorder.json**::

    add_schedule_config(ts, command="python -c \"print('hello test')\"", node_group_name='idm_abcd', num_cores=2,
                            NumProcesses=1, NumNodes=1,
                            Environment={"key1": "value1", "key2:": "value2"})


.. _Examples:

Example
-------

For addition information and specifics of using a workorder.json file within Python, you can begin with the following:

.. literalinclude:: ../../../examples/python_model/python_sim_scheduling_hpc.py
    :language: python

.. _Schemas:

Schemas
-------

The following schemas, for both HPC and SLURM clusters on |COMPS_s|, list the available options you are able to include within the workorder.json file.

**HPC**::

    {
      "title": "MSHPC job WorkOrder Schema",
      "$schema": "http://json-schema.org/draft-04/schema",
      "type": "object",
      "required": [
        "Command"
      ],
      "properties": {
        "Command": {
          "type": "string",
          "minLength": 1,
          "description": "The command to run, including binary and all arguments"
        },
        "NodeGroupName": {
          "type": "string",
          "minLength": 1,
          "description": "The cluster node-group to commission the job to"
        },
        "NumCores": {
          "type": "integer",
          "minimum": 1,
          "description": "The number of cores to reserve"
        },
        "SingleNode": {
          "type": "boolean",
          "description": "A flag to limit all reserved cores to being on the same compute node"
        },
        "Exclusive": {
          "type": "boolean",
          "description": "A flag that controls whether nodes should be exclusively allocated to this job"
        }
      },
      "additionalProperties": false
    }

**SLURM**::

    {
      "title": "SLURM job WorkOrder Schema",
      "$schema": "http://json-schema.org/draft-04/schema",
      "type": "object",
      "required": [
        "Command"
      ],
      "properties": {
        "Command": {
          "type": "string",
          "minLength": 1,
          "description": "The command to run, including binary and all arguments"
        },
        "NodeGroupName": {
          "type": "string",
          "minLength": 1,
          "description": "The cluster node-group to commission to"
        },
        "NumCores": {
          "type": "integer",
          "minimum": 1,
          "description": "The number of cores to reserve"
        },
        "NumNodes": {
          "type": "integer",
          "minimum": 1,
          "description": "The number of nodes to schedule"
        },
        "NumProcesses": {
          "type": "integer",
          "minimum": 1,
          "description": "The number of processes to execute"
        },
        "EnableMpi": {
          "type": "boolean",
          "description": "A flag that controls whether to run the job with mpiexec (i.e. whether the job will use MPI)"
        },
        "Environment": {
          "type": "object",
          "description": "Environment variables to set in the job environment; these can be dynamically 
          expanded (e.g. $PATH)",
          "additionalProperties": {
            "type": "string"
          }
        }
      },
      "additionalProperties": false
    }
