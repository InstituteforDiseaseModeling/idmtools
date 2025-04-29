===================================
Architecture and packages reference
===================================


|IT_s| is built in Python and includes an architecture designed for ease of use, flexibility, and extensibility. You can quickly get up and running and see the capabilities of |IT_s| by using one of the many included example Python scripts demonstrating the functionality of the packages.

|IT_s| is built in a modular fashion, as seen in the diagrams below. |IT_s| design includes multiple packages and APIs, providing both the flexibility to only include the necessary packages for your modeling needs and the extensibility by using the APIs for any needed customization.

Packages overview
=================

.. uml:: /diagrams/packages_overview.puml


Packages and APIs
=================

The following diagrams help illustrate the primary packages and associated APIs available for modeling and development with |IT_s|:

Core and job orchestration
--------------------------

.. uml:: /diagrams/core.puml


|CONTAINER_s| Platform
----------------------

.. uml:: /diagrams/platform_container.puml


|COMPS_s| platform
------------------

.. uml:: /diagrams/comps.puml

.. include:: /reuse/comps_note.txt

|SLURM_s| platform
------------------

.. uml:: /diagrams/slurm.puml


Models reference
----------------

.. uml:: /diagrams/models.puml

API class specifications
------------------------

.. uml:: /diagrams/apis.puml

|EMOD_s|
^^^^^^^^

.. uml:: /diagrams/apis-emod.puml

|EMOD_s| support with |IT_s| is provided with the **emodpy** package, which leverages |IT_s| plugin architecture.


API Documentation
=================
.. toctree::
   :maxdepth: 3
   :titlesonly:

   api/idmtools_index
   api/idmtools_models_index
   api/idmtools_platform_comps_index
   api/idmtools_platform_slurm_index
   api/idmtools_platform_container_index