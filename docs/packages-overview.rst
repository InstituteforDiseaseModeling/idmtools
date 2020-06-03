=================
Packages overview
=================

|IT_s| is built in a modular fashion, as seen in the diagram below. Because of this, to get select functionality requires including multiple packages within your Python scripts.

.. uml::

    @startuml
    [idmtools]
    note right of idmtools
    Provides Plugin Infrastructure and
    common APIS like Experiments,
    Simulations, Suites, Workitems,
    Tasks, and Platforms. Also contains
    tools for building Simulations in bulk
    end note

    [idmtools-cli]
    note left of [idmtools-cli]
    Provides the CLI for
    idmtools. (Optional)
    end note

    [idmtools-models]
    note right of [idmtools-models]
    Provides common tasks
    for Python and R
    end note

    [idmtools-platform-comps]
    note left of [idmtools-platform-comps]
    Provides ability to
    interact with COMPS
    end note

    [idmtools-platform-local]
    note left of [idmtools-platform-local]
    Provides ability to run
    locally using Docker containers
    end note

    [idmtools-cli] --> [idmtools]
    [idmtools-models] --> [idmtools]
    [idmtools-platform-comps] -> idmtools
    [idmtools-platform-local] -up-> idmtools
    @enduml

For more information about the packages and associated classes see the following API documentation:

* :any:`idmtools<idmtools_index>`
* :any:`idmtools-models<idmtools_models_index>`
* :any:`idmtools-platform-comps<idmtools_platform_comps_index>`
* :any:`idmtools-platform-local<idmtools_platform_local_index>`
* :any:`idmtools-cli<cli_index>`

For detailed architectural information and diagrams see :doc:`architecture`