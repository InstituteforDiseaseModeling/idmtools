========
Glossary
========


The following terms describe both the features and functionality of the |IT_s| software, as well
as information relevant to using |IT_s|.

.. glossary::
    :sorted:

    analyzer
        Functionality that uses the MapReduce framework to process large data sets in parallel, typically on a :term:`high-performance computing (HPC)` cluster. For example, if you would like to focus on specific data points from all simulations in one or more experiments then you can do this using analyzers with |IT_s| and plot the final output.

    asset collection
        A collection of user created input files, such as demographics, temperature, weather, binaries, and overlay files. These files are stored in |COMPS_s| and can be available for use by other users.

    assets
        See :term:`asset collection`.

    builder
        A function and list of values with which to call that function that is used to sweep through parameter values in a simulation.

    calibration
        The process of adjusting the parameters of a simulation to better match the data from a particular time and place. 

    entity
        Each of the interfaces or classes that are well-defined models, types, and validations for |IT_s| items, such as simulations, analyzers, or tasks.

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
        The computing resource on which the simulation runs. See :doc:`platforms/platforms` for
        more information on those that are currently supported. 

    simulation
        An individual run of a model. Generally, multiple simulations are run as part
        of an experiement. 

    server-side modeling tools (SSMT)
        Modeling tools used with |COMPS_s| that handle computation on the server side, rather than the client side, to speed up analysis. 

    suite
        Logical grouping of experiments. This allows for managing multiple experiments as a single unit or grouping.
        
    task
        The individual actions that are processed for each simulation.

    container
        A Docker container that includes a Linux operating system, Python 3.9, MPICH, and all necessary dependencies. This container is used to run the |IT_s| software.

        .. Is this correct?

