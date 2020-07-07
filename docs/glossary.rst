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
        Collection of user created input files, such as demographics, temperature, weather, and overlay files. These files are stored in |COMPS_s| and can be available for use by other users.

    assets
        See :term:`asset collection`.

    builder
        Functionality that builds experiments using templated simulations.

        .. Can you provide more detail? This doesn't seem that clear to me. 

    calibration
        The process of adjusting the parameters of a simulation to better match the data from a particular time and place. 

    entity
        Each of the items, such as simulations, analyzers, or tasks, that are managed by |IT_s|.

        .. Is this correct? Total stab in the dark. 

    |EMOD_s|
        An agent-based mechanistic disease transmission model built by |IDM_s| that can be used with |IT_s|. See the `EMOD GitHub repo <https://github.com/InstituteforDiseaseModeling/EMOD>`_.

    experiment
        Logical grouping of simulations. This allows for managing numerous simulations as a single unit or grouping.

    high-performance computing (HPC)
        The use of parallel processing for running advanced applications efficiently, reliably,
        and quickly.

    parameter sweep
        An iterative process in which simulations are run repeatedly using different values of the parameter(s) of choice. This process enables the modeler to determine what a parameter’s “best” value or range of values.

    platform
        The computing resource on which the simulation runs. See :doc:`platforms` for
        more information on those that are currently supported. 

    simulation
        An individual run of a model. Generally, multiple simulations are run as part
        of an experiement. 

    server-side modeling tools (SSMT)
        Modeling tools used with |COMP_s| that handle computation on the server, rather than the client, side to speed up analysis. 

    suite
        Logical grouping of experiments. This allows for managing multiple experiments as a single unit or grouping.
        
    task
        The individual actions that are processed for each simulation.

        .. Is this correct?

