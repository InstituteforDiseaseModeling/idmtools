=========================
Convert scripts from |DT|
=========================
Understanding some of the similarities and differences between |DT| and |IT_s|
will help when converting scripts from |DT| to use within |IT_s|.

Configuration .ini files have different names, **simtools.ini** in |DT| and
**idmtools.ini** in |IT_s|; and, simtools.ini is required while idmtools.ini is
optional.

Platform configuration, HPC or local, in |DT| is set using the
:py:class:`SetupParser` class while in |IT_s| the
:py:class:`~idmtools.core.platform_factory.Platform` class is used.

Simulation configuration, such as intervention parameters and reports, in |DT|
are set using the :py:class:`DTKConfigBuilder` class while in |IT_s| it's configured
through a base task object.

Configuration .ini files
========================
Please see the following diagram which helps illustrate some of the differences
between the required **simtools.ini** used in |DT| with the optional **idmtools.ini**
used in |IT_s|.

.. uml::

    hide circle

    note top of simtools
    DTK-Tools
    end note

    class simtools{
        [DEFAULT]
        max_threads = 1
        sims_per_threads = 1
        max_local_sims = 6
        server_endpoint = https://comps.idmod.org
        environment = Belegost

        [HPC]
        type = HPC
    }

    note top of idmtools
    idmtools
    end note

    class idmtools{
        [COMPS]
        priority = Lowest
        num_retries = 0
        batch_size = 10
        endpoint = https://comps.idmod.org
        environment = Belegost
        type = COMPS
    }

    idmtools -left[hidden]-> simtools


Platform configuration
======================
In addition to using ini files for platform configuration parameters you can also
use Python class objects, :py:class:`SetupParser` in |DT| and
:py:class:`~idmtools.core.platform_factory.Platform` in |IT_s|. If platform configuration
parameters are configured in an ini file and also configured in a Python class object
then the parameters in the Python object take priority.

**DTK-Tools**::

    SetupParser.default_block = 'HPC'

**idmtools**::

    platform = Platform("Belegost")

When using :py:class:`~idmtools.core.platform_factory.Platform` you can specify
a predefined configuration alias, such as `Belegost`, when using the
|COMPS_s| platform. To see a list of aliases, use the cli command
*idmtools info plugins platform-aliases*.

Simulation configuration
========================

:py:class:`DTKConfigBuilder` in |DT| is used for setting the intervention parameters
and reports for simulations run with |DT| while |IT_s| uses task objects. For example,
when using |EMODPY_s| the :py:class:`~emodpy.emod_task.EMODTask` class is used.

.. uml::

    hide circle

    note top of DTKConfigBuilder
    DTK-Tools
    end note

    class DTKConfigBuilder{
        config
        campaign
        demographics
        report
    }

    note top of EMODTask
    idmtools/emodpy
    end note

    class EMODTask{
        task.config
        task.campaign
        task.demographics
        task.reporter
    }

    EMODTask -left[hidden]-> DTKConfigBuilder


Example
=======
To see an applied example of the previously described information you can see a
converted |DT| csv analyzer to |IT_s| and addition information on
converting analyzers here: :doc:`analyzers/analyzers-convert`.