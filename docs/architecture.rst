============
Architecture
============

|IT_s| is built in Python and includes an architecture designed for ease of use, flexibility, and extensibility. You can quickly get up and running and see the capabilities of |IT_s| by using one of the many included example Python scripts demonstrating the functionality of the packages. |IT_s| design includes multiple packages and APIs, providing both the flexibility to only include the necessary packages for your modeling needs and the extensibility by using the APIs for any needed customization.

Packages overview
=================

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

Packages and APIs 
=================

The following diagrams help illustrate the primary packages and associated APIs available for modeling and development with |IT_s|:

Core and job orchestration
--------------------------

.. uml::

    @startuml

    [Analyzers]
    package "Experiment/Job Orchestration     " as ejo {
        [Assets]
        [Experiment]
        [ExperimentBuilders]
        [Simulation]
        [Tasks]
        [Platform]
        [Suite]
    }

    package "registry (Plugin Infrastructure)     " as registry {
        () "PlatformAPI" as PlatformAPI
        () "TasksAPI" as TasksAPI
    }

    package "Tasks " as tasks {
        [CommandTask]
        [DockerTask]
    }

    Analyzers .. Platform: Load Data from Platform
    ExperimentBuilders . Experiment: ExperimentBuilders build \nexperiments using \ntemplated simulations
    ExperimentBuilders . Simulation : ExperimentBuilders\n uses Simulations from\n TemplatedSimulations
    Platform --> PlatformAPI
    PlatformAPI .. TasksAPI
    [Suite] -down-> Experiment : Suites have Experiments
    [Assets] <.> Platform : Load/Create
    [Experiment] <.down.> Platform : Load/Create
    [Experiment] -down-> Simulation
    [Experiment] -right-> [Assets] : Experiment\nAssets
    [Simulation] -> Assets: Simulation-level Assets
    [Simulation] <.> Platform : Load/Create
    [Simulation] -down-> [Tasks] : All Simulation\nhave tasks
    [Tasks] -> Assets : Tasks Assets
    [Tasks] <---> TasksAPI : Uses API
    TasksAPI <-right-- CommandTask : Implements as\na Generic Task
    TasksAPI <-down-- DockerTask: Implements Python-based Tasks
    @enduml

Local platform
--------------

.. uml::

    @startuml
    package "idmtools-cli" as cli {
        [CLI]
        () "CLI API" as cli_api
    }

    package "idmtools-core" as registry {
        () "PlatformAPI" as PlatformAPI
    }

    package "idmtools-platform-local" as local {
        [LocalPlatform]
        [LocalPlatformCLI]
    }

    PlatformAPI <-down-> LocalPlatform : LocalPlatform Implementation
    cli_api <.> LocalPlatformCLI : idmtools local commands
    LocalPlatformCLI <--> LocalPlatform
    LocalPlatform -[hidden]- LocalPlatformCLI
    @enduml

|COMPS_s| platform
----------------

.. uml::

    @startuml

    package "idmtools-core" as registry {
        () "PlatformAPI" as PlatformAPI
    }

    package "idmtools-platform-comps" as comps {
        [COMPSPlatform]
        [SSMTPlatform]
    }

    PlatformAPI <-down-- COMPSPlatform: COMPs\nImplementation
    PlatformAPI <-- SSMTPlatform: SSMT\nImplementation
    @enduml

.. note::

    To access and use |COMPS_s| you must receive approval and credentials from |IDM_s|. Send your request to support@idmod.org.

Models
------

.. uml::

    @startuml

    package "idmtools-core" as registry {
        () "TasksAPI" as TasksAPI
    }

    package "idmtools-models" as models {
        [PythonTask]
        [JSONConfiguredPythonTask]
        [RTask]
        [JSONConfiguredRTask]
        PythonTask <-- JSONConfiguredPythonTask: Adds JSON configuration\n file to PythonTask
        RTask <-- JSONConfiguredRTask: Adds JSON configuration\n file to PythonTask
    }

    TasksAPI <-- PythonTask: Implements Python-based Tasks
    TasksAPI <- RTask : Implements R-based Tasks
    @enduml

API class specifications
------------------------

.. uml::

    @startuml

    package "idmtools" {
        class PluginSpecification {
            str get_name(strip_all)
            {abstract} str get_description()
            List[ProjectTemplate] get_project_templates()
            List[str] get_example_urls()
            Dict[str, str] get_help_urls()
            {static} get_version_url(version, repo_base_url, nightly_branch)
        }

        class TaskSpecification {
            {abstract} Type[ITask] get_type()
            {abstract} ITask get()
        }

        class PlatformSpecification {
            {abstract} Type[IPlatform] get_type()
            {abstract} IPlatform get()
        }
    }

    package "cli"{
        class PlatformCLISpecification {
            {abstract} Type[IPlatformCLI] get_type()
            {abstract} PlatformCLI get()
        }
    }

    PluginSpecification <-- TaskSpecification
    PluginSpecification <-- PlatformSpecification
    PluginSpecification <-- PlatformCLISpecification
    @enduml
