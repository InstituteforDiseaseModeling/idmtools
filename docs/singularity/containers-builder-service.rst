=========================
Container builder service
=========================

The container builder service in |IT_s| uses the 
:py:class:`~idmtools_platform_comps.utils.singularity_build.SingularityBuildWorkItem`
class, which can use as input a .def (Singularity container defiinition) file 
(the instructions or blueprint for building the container - .sif file), and then 
writes it to an asset collection id file to be available as part of an asset collection on 
|COMPS_s|. You can then use the built container for running simulations on |COMPS_s|.

For more information about Singularity builds on |COMPS_s|, see :doc:`/platforms/comps/singularity_build`.


.. Supported features
.. ------------------
.. Clinton to provide list


.. Building a container workflow
.. =============================
.. Clinton, Ross 


.. Client caching implementation
.. =============================
.. Clinton


.. Examples
.. ========
.. The following container builder services examples are included:

.. * Build Python Container
.. * Build R Container

.. Build Python Container
.. ----------------------
.. (Sharon/Clinton)

.. Build R Container
.. -----------------
.. (Lauren/Sharron)
