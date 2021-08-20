=================
Welcome to |IT_s|
=================

|IT_s| is a collection of Python scripts and utilities created to streamline user interactions with
disease models. This framework provides the user with tools necessary to complete projects, starting
from the creation of input files (if required), to calibration of the model to data, to commissioning
and running simulations, through the analysis of results. Modelers can use |IT_s| to run models
locally or send suites of simulations to an HPC or other computing source. This framework is
free, open-source, and model agnostic: it can be used to interact with a variety of models,
such as custom models written in R or Python, or IDM's own |EMOD_s|. Additional functionality 
for interacting with |EMOD_s| is provided in the :doc:`emod_api:emod_api_index` and 
:doc:`emodpy:emodpy_index` packages.



|IT_s| workflow
===============

.. high level overview of what the tools do

|IT_s| includes a variety of options for each step of the modeling process. Because of this, the
tool suite was developed in a modular fashion, so that users can select the utilities they wish
to use. In order to simplify the desired workflow, facilitate the modeling process, and make the
model (and its results) reusable and sharable, |IT_s| allows the user to create :term:`assets`.
Assets can be added at any level of the process, from running a specific task, through creating
a simulation, to creating a :term:`experiment`. This allows the user to create inputs based on their
specific needs: they can be transient, or sharable across multiple simulations.

.. To help new users get started, a series of Cookiecutter projects have been added, designed to
.. guide modelers through necessary tasks. See :doc:`cookiecutters` for the available templates.

The diagram below shows how |IT_s| and each of the related packages are used in
an end-to-end workflow using |EMOD_s| as the disease transmission model.


.. uml::

   hide stereotype
   skinparam component {
     BackgroundColor<<emodpy-disease>> F9BA9D
     BackgroundColor<<idmtools>> 006CA6
     BackgroundColor<<calibration>> gray
     BackgroundColor<<emodpy-core>> F18153
     BackgroundColor<<COMPS>> lightgray
     BackgroundColor<<EMOD>> 47C8F5
   }


   [emodpy-generic] <<emodpy-disease>>
   [emodpy-generic] --> [emodpy]

   [emodpy-hiv] <<emodpy-disease>>
   [emodpy-hiv] --> [emodpy]

   [emodpy-malaria] <<emodpy-disease>>
   [emodpy-malaria] --> [emodpy]

   [emodpy-measles] <<emodpy-disease>>
   [emodpy-measles] --> [emodpy]

   [emodpy-tbhiv] <<emodpy-disease>>
   [emodpy-tbhiv] --> [emodpy]


   [emodpy] <<emodpy-core>>
   [emod-api] <<emodpy-core>>
   [emodpy] --> [emod-api]

   [emodpy] <-> [idmtools]

   [idmtools] <<idmtools>>
   [COMPS] <<COMPS>>
   [idmtools] <-> [COMPS] : Commission and status

   [idmtools-calibra] <<calibration>>
   [idmtools-calibra] <--> [idmtools] : Commission and analysis
   [idmtools-calibra] <--> [emodpy] : Calibration

   [emodpy-calibra] <<calibration>>
   [emodpy-calibra] <--> [emodpy]: EMOD-specific calibration utils
   [emodpy-calibra] <--> [idmtools-calibra]
   [Input files] <<EMOD>>
   [emod-api] --> [Input files] : Create

   [Input files] ..> [emod-api] : Inspect

   [EMOD Eradication.exe] <<EMOD>>
   [Input files] -> [EMOD Eradication.exe]

   [Output files] <<EMOD>>
   [EMOD Eradication.exe] -> [Output files]
   [Output files] --> [emod-api]


Exact workflows for using |IT_s| is user-dependent, and can include any of the tasks listed below.

.. toctree::
   :maxdepth: 3
   :titlesonly:

   installation
   configuration
   platforms/platforms
   create-sims
   containers/containers
   parameter-sweeps
   reports
   analyzers/analyzers
   plots   
   reference
   recipes_index
   cli/cli_index
   dtkt-convert
   faq
   glossary
   changelog/changelog



.. not sure what to do with catalyst. Not included yet.

.. nothing done with STAMP yet; not sure if it will be some sort of "plug-in" to the tools or totally standalone

.. Nothing here for EMOD API. We'll want to put it *somewhere* and likely have a landing page for it here...

