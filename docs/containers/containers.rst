===================
Containers overview
===================

You can use |IT_s| in containers, such as Singularity and |COMPS_s|. This can help 
make it easier for other data scientists to use and rerun your work without having 
to try and reproduce your environment and utilities. You just need to share your 
container for others to run on their own HPC. 

"A container is a software package that contains everything the software needs to run. 
This includes the executable program as well as system tools, libraries, and settings", 
as quoted from techterms.com (https://techterms.com/definition/container). The conceptual 
components of containers are the same regardless of the specific container technology, such 
as Singularity and Docker.

For additional overview and conceptual information about containers, see the following:

* Containers (https://www.ibm.com/cloud/learn/containers)
* Understanding Linux containers (https://www.redhat.com/en/topics/containers)
* Containers and Dockers for Data Scientist (https://medium.com/ai-for-real/containers-and-dockers-for-data-scientist-c9000fb69478)


Containers and science
----------------------

Containers and science are great partners. The primary reason being the enhancement of reproducibility 
in scientific computing. Another reason is to allow access to more utilities beyond the scope of 
what is available by default within your HPC environments. For example, if you need to use the Julia 
programming language or any other utilities not currently available in your HPC then you could create 
your own container with the desired utilities. This allows you control over the environment and tools 
in the container to be run on your HPC.


Understand Singularity
----------------------

"Singularity is a free, cross-platform and open-source computer program that performs operating-system-level 
virtualization also known as containerization. One of the main uses of Singularity is to bring containers and 
reproducibility to scientific computing and the high-performance computing world.", as quoted from 
https://en.wikipedia.org/wiki/Singularity_(software).

For additional overview and conceptual information about Singularity, see the following:

* Introduction to Singularity (https://sylabs.io/guides/3.7/user-guide/introduction.html)
* About Singularity (https://singularity.lbl.gov/about)
* Singularity (https://singularity.lbl.gov/)


.. toctree::
    containers-services
    containers-builder-service
    containers-comps