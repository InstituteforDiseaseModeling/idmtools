===================================
Architecture and packages reference
===================================


|IT_s| is built in Python and includes an architecture designed for ease of use, flexibility, and extensibility. You can quickly get up and running and see the capabilities of |IT_s| by using one of the many included example Python scripts demonstrating the functionality of the packages.

|IT_s| is built in a modular fashion, as seen in the diagrams below. |IT_s| design includes multiple packages and APIs, providing both the flexibility to only include the necessary packages for your modeling needs and the extensibility by using the APIs for any needed customization.

Packages overview
=================

.. image:: /diagrams/packages_overview.png
   :alt: Packages Overview
   :align: center


Packages and APIs
=================

The following diagrams help illustrate the primary packages and associated APIs available for modeling and development with |IT_s|:

Core and job orchestration
--------------------------

.. image:: /diagrams/core.png
   :alt: Core
   :align: center


|CONTAINER_s| Platform
----------------------

.. image:: /diagrams/platform_container.png
   :alt: Container Platform
   :align: center

|COMPS_s| platform
------------------

.. image:: /diagrams/comps.png
   :alt: Comps Platform
   :align: center

.. include:: /reuse/comps_note.txt

|SLURM_s| platform
------------------

.. image:: /diagrams/slurm.png
   :alt: Slurm Platform
   :align: center


Models reference
----------------

.. image:: /diagrams/models.png
   :alt: Models
   :align: center

API class specifications
------------------------

.. image:: /diagrams/apis.png
   :alt: API class
   :align: center

|EMOD_s|
^^^^^^^^

.. image:: /diagrams/apis-emod.png
   :alt: emod-api
   :align: center

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