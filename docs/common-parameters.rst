Global Parameters
=================

There are a few global parameters that drive features within  IDM-Tools.  These mainly control features around workers
and threads and are defined within the GLOBAL configuration section. Most likely, you will not need to change these.

* max_threads - The defines the maximumnNumber of threads idm-tools will use for analysis and other multi-threaded activities. Defaults to 16.
* sims_per_thread - How many simulations per threads during simulation creation. Defaults to 20.
* max_local_sims - Maximum simulations to run locally
* max_workers - Maxium number of workers processing in parallel. Defaults to 16.
* batch_size - Maxium batch size to retrieve simulations. Defaults to 10