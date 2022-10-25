Global parameters
=================

The idmtool.ini file includes some global parameters that drive features within |IT_s|. These primarily control features around workers
and threads and are defined within the [COMMON] section of idmtool.ini. Most likely, you will not need to change these.

The following includes an example of the [COMMON] section of idmtools.ini with the default settings::

    [COMMON]
    max_threads = 16
    sims_per_thread = 20
    max_local_sims = 6
    max_workers = 16
    batch_size = 10

* max_threads - Maximum number of threads for analysis and other multi-threaded activities.
* sims_per_thread - How many simulations per threads during simulation creation.
* max_local_sims - Maximum simulations to run locally.
* max_workers - Maximum number of workers processing in parallel.
* batch_size - Maximum batch size to retrieve simulations.
