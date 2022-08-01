===================
Supported Platforms
===================

|IT_s| currently supports running on the following platforms:

**COMPS**: |COMPS_l| is a high performance computing cluster used by employees and collaborators at |IDM_s|. To support running simulations and analysis on |COMPS_s|, |IT_s| includes the following modules: :doc:`../idmtools_platform_comps_index`.

.. include:: /reuse/comps_note.txt

**Local**: You can also run simulations and analysis locally on your computer, rather than on a remote high-performance computer (HPC). For more information about these modules, see :doc:`../idmtools_platform_local_index`.

You can use the **idmtools.ini** file to configure platform specific settings, as the following examples shows for |COMPS_s|::

    [COMPS]
    type = COMPS
    endpoint = https://comps.idmod.org
    environment = Belegost
    priority = Lowest
    simulation_root = $COMPS_PATH(USER)\output
    node_group = emod_abcd
    num_retires = 0
    num_cores = 1
    max_workers = 16
    batch_size = 10
    exclusive = False

As an alternative to the INI based configurations, some platforms such as COMPS provide predefined configurations aliases. With those aliases, you can use an alias for a known environment without a config. To see a list of aliases, use the cli command *idmtools info plugins platform-aliases*.

Within your code you use the :py:class:`~idmtools.core.platform_factory.Platform` class to specify which platform |IT_s| will use. For example, the following excerpt sets **platform** to use |COMPS_s| and overrides **priority** and **node_group** settings.::

    platform = Platform('COMPS',priority='AboveNormal',node_group='emod_a')

You use the :py:class:`~idmtools.core.platform_factory.Platform` class whether you're building or running an experiment, or running analysis on output from simulations.

For additional information about configuring idmtools.ini, see :doc:`../configuration`.

.. toctree::
   platforms-comps
   platforms-slurm
   platforms-local
   platforms-plugin
