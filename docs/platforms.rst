=========
Platforms
=========

|IT_s| currently supports running on the following platforms:

| **COMPS**: |COMPS_l| is a high performance computing cluster used by employees and collaborators at |IDM_s|. To support running simulations and analysis on |COMPS_s|, |IT_s| includes the following modules: :doc:`idmtools_platform_comps_index`.

| **Local**: You can also run simulations and analysis locally on your computer, rather than on a remote high-performance computer (HPC). For more information about these modules, see :doc:`idmtools_platform_local_index`.

You can use the **idmtools.ini** file to configure platform specific settings, as the following examples shows for |COMPS_s|::

    [COMPS2]
    type = COMPS
    endpoint = https://comps2.idmod.org
    environment = Bayesian
    priority = Lowest
    simulation_root = $COMPS_PATH(USER)\output
    node_group = emod_abcd
    num_retires = 0
    num_cores = 1
    max_workers = 16
    batch_size = 10
    exclusive = False

Within your code you use the :py:class:`~idmtools.core.platform_factory.Platform` class to specify which platform |IT_s| will use. For example, the following excerpt sets **platform** to use |COMPS_s|::

    platform = Platform('COMPS2')

You use the :py:class:`~idmtools.core.platform_factory.Platform` class whether you're building or running an experiment, or running analysis on output from simulations.

For additional information about configuring idmtools.ini, see...

Note for the creation of platforms: If you are developing a new platform plugin, you will need to add some metadata to the Platform class' fields.
All fields with a ``help`` key in the metadata will be picked up by the ``idmtools config block`` command line and allow a user to set a value.
``help`` should contain the help text that will be displayed.
A ``choices`` key can optionally be present to restrict the available choices.

For example, for the given platform:
.. code-block:: python

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        field1: int = field(default=1, metadata={"help": "This is the first field"})
        internal_field: imt = field(default=2)
        field2: str = field(default="a", metadata={"help": "this is the second field", "choices": ["a", "b", "c"]})


The CLI wizard will pick up ``field1`` and ``field2`` and ask the user to provide values. The type of the field will be enforced and for ``field2``, the user will have to select among the ``choices``.

Now, what happens if we want to change the help text, choices, or default value of a field based on a previously set field.
For example, let's consider an example platform where the user needs to specify an endpoint. This endpoint needs to be used to retrieve a list of environments and we want the user to choose select one of them.

.. code-block:: python

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        endpoint: str = field(default="https://myapi.com", metadata={"help": "Enter the URL of the endpoint"})
        environment: str = field(metadata={"help": "Select an environment "})

The list of environments is dependant on the endpoint value. To achieve this, we need to provide a ``callback`` function to the metadata.
This function will receive all the previously set user parameters, and will have the opportunity to modify the current field's ``choices``, ``default``, and ``help`` parameters.

Let's create a function querying the endpoint to get the list of environments and setting them as choices. Selecting the first one as default.

.. code-block:: python

    def environment_list(previous_settings:Dict, current_field:Field) -> Dict:
        """
        Allows the CLI to provide a list of available environments.
        Uses the previous_settings to get the endpoint to query for environments
        Args:
            previous_settings: previous settings set by the user in the CLI.
            current_field: Current field specs

        Returns: updates to the choices and default
        """
        # Retrieve the endpoint set by the user
        # The key of the previous_settings is the name of the field we want the value of
        endpoint = previous_settings["endpoint"]

        # Query the API for environments
        client.connect(endpoint)
        environments = client.get_all_environments()

        # If the current field doesnt have a set default already, set one by using the first environment
        # If the field in the platform class has a default, consider it first
        if current_field.default not in environments:
            default_env = environment_choices[0]
        else:
            default_env = current_field.default

        # Return a dictionary that will be applied to the current field
        # Setting the new choices and default at runtime
        return {"choices": environment_choices, "default": default_env}


We can then use this function on the field, and the user will be prompted with the correct list of available environments.

.. code-block:: python

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        endpoint: str = field(default="https://myapi.com", metadata={"help": "Enter the URL of the endpoint"})
        environment: str = field(metadata={"help": "Select an environment ", "callback": environment_list})
