========
Glossary
========


The following terms describe both the features and functionality of the |IT_s| software, as well
as information relevant to using |IT_s|.

.. glossary::
    :sorted:

    analyzer
        Functionality that uses the the MapReduce framework to process large data sets in parallel, typically on a :term:`high-performance computing (HPC)` cluster. For example, if you would like to focus on specific data points from all simulations in one or more experiments then you can do this using analyzers with |IT_s| and plot the final output.

    asset collection
        The set of specific input files (such as input parameters, weather or
        migration data, or other configuration settings) required for running
        a simulation.

        .. Is this specific to COMPS? 

    assets
        See :term:`asset collection`.

    builder
        Functionality that builds experiments using templated simulations.

        .. Can you provide more detail? This doesn't seem that clear to me. 

    calibration
        The process of adjusting the parameters of a simulation to better match the data from a particular time and place. 

    entities
        The items, such as simulations, analyzers, or tasks, that are managed by |IT_s|

        .. Is this correct? Total stab in the dark. 

    |EMOD_s|
        An agent-based mechanistic disease transmission model built by |IDM_s| that can be used with |IT_s|. See the `EMOD GitHub repo <https://github.com/InstituteforDiseaseModeling/EMOD>`_.

    experiment
        A collection of multiple simulations, typically sent to an HPC.

    high-performance computing (HPC)
        The use of parallel processing for running advanced applications efficiently, reliably,
        and quickly.

    platform
        The computing resource on which the simulation runs. See :doc:`platforms` for
        more information on those that are currently supported. 

    simulation
        An individual run of a model. Generally, multiple simulations are run as part
        of an experiement. 

    SSMT
        TBD

    suite
        A collection of multiple experiments, each of which contains multiple simulations. 
        
    task
        All simulations have tasks.

        What does this mean exactly? 

    template
        TBD

