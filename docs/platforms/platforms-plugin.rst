======================
Create platform plugin
======================

You can add a new platform to |IT_s| by creating a new platform plugin, as described in the following sections:

Adding fields to the config CLI
```````````````````````````````

If you are developing a new platform plugin, you will need to add some metadata to the Platform class' fields.
All fields with a ``help`` key in the metadata will be picked up by the ``idmtools config block`` command line and allow a user to set a value.
``help`` should contain the help text that will be displayed.
A ``choices`` key can optionally be present to restrict the available choices.

For example, for the given platform:

.. code-block:: python

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        field1: int = field(default=1, metadata={"help": "This is the first field."})
        internal_field: imt = field(default=2)
        field2: str = field(default="a", metadata={"help": "This is the second field.", "choices": ["a", "b", "c"]})


The CLI wizard will pick up ``field1`` and ``field2`` and ask the user to provide values. The type of the field will be enforced and for ``field2``, the user will have to select among the ``choices``.

Modify fields metadata at runtime
`````````````````````````````````

Now, what happens if we want to change the help text, choices, or default value of a field based on a previously set field?
For example, let's consider an example platform where the user needs to specify an endpoint. This endpoint needs to be used to retrieve a list of environments and we want the user to choose select one of them.

.. code-block:: python

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        endpoint: str = field(default="https://myapi.com", metadata={"help": "Enter the URL of the endpoint."})
        environment: str = field(metadata={"help": "Select an environment."})

The list of environments is dependent on the endpoint value. To achieve this, we need to provide a ``callback`` function to the metadata.
This function will receive all the previously set user parameters, and will have the opportunity to modify the current field's ``choices``, ``default``, and ``help`` parameters.

Let's create a function querying the endpoint to get the list of environments and setting them as choices. Selecting the first one as default.

.. code-block:: python

    def environment_list(previous_settings:Dict, current_field:Field) -> Dict:
        """
        Allows the CLI to provide a list of available environments.
        Uses the previous_settings to get the endpoint to query for environments.
        Args:
            previous_settings: Previous settings set by the user in the CLI.
            current_field: Current field specs.

        Returns: 
            Updates to the choices and default.
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

Fields validation
`````````````````

By default the CLI will provide validation on type. For example an ``int`` field, will only accept an integer value.
To fine tune this validation, we can leverage the ``validation`` key of the metadata.

For example, if you want to create a field that has an integer value between 1 and 10, you can pass a validation function as shown:

.. code-block:: python

    def validate_number(value):
        if 1 <= value <= 10:
            return True, ''
        return False, "The value needs to be bewtween 1 and 10."

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        custom_validation: int = field(default=1, metadata={"help": "Enter a number between 1 and 10.", "validation":validate_number})

The validation function will receive the user input as ``value`` and is expected to return a ``bool`` representing the result of the validation
(``True`` if the value is correct, ``False`` if not) and a ``string`` to give an error message to the user.

We can leverage the `Python partials <https://docs.python.org/3.7/library/functools.html#functools.partial>`_ and make the validation function more generic to use
in multiple fields:

.. code-block:: python

    from functools import partial

    def validate_range(value, min, max):
        if min <= value <= max:
            return True, ''
        return False, f"The value needs to be between {min} and {max}."

    @dataclass(repr=False)
    class MyNewPlatform(IPlatform, CacheEnabled):
        custom_validation: int = field(default=1, metadata={"help": "Enter a number between 1 and 10.", "validation":partial(validate_range, min=1, max=10)})
        custom_validation2: int = field(default=100, metadata={"help": "Enter a number between 100 and 500.", "validation":partial(validate_range, min=100, max=500)})