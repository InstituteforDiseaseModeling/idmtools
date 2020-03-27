=================
Welcome to |IT_s|
=================

|IT_l| is a set of python tools...


.. toctree::
   :maxdepth: 3
   :titlesonly:

   overview
   installation
   core
   local
   models
   examples
   reference
   glossary


.. we'll want to figure out how to organize the high-level TOC, since we want topics to be
.. FINDABLE, but also to have the repo organization make sense. Currently (as of 6-12-19), repo has:
.. examples (examples and jupyter notebooks)
.. idmtools_core (this is wehre a lot of the actual services will be, such as calibration)
.. idmtools_local_runner (the service to run things locally)
.. idmtools_models_collection (which contains python and dtk stuff at this point. Where model-specific utils located, eg config-builder)


.. not sure how all of the nesting will work. For example: for ANALYZERS, will this be a high-level
.. topic, or will it get nested in the "dtk" section under models (for the custom utilities)?
.. as of now, have calibration under "core," analyzers, sweeps, run, create, etc under "models/dtk"

.. currently don't have anything set up for the API reference docs, but added in a placeholder file

.. not sure what to do with catalyst. Not included yet.


.. we will want to keep an eye on the "local platform" stuff--since it's an entire section of the repo,
.. I pulled it out for top level TOC placement. However, if that's for ease of code and not something
.. more complicated, let's take Jen's suggestion and nest it within each model