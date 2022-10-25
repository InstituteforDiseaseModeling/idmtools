"""idmtools cli utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from dataclasses import Field
from typing import Dict, Tuple


def validate_range(value: float, min: float, max: float) -> Tuple[bool, str]:
    """
    Function used to validate an integer value between min and max.

    Args:
        value: The value set by the user
        min: Minimum value
        max: Maximum value

    Returns: tuple with validation result and error message if needed
    """
    if min <= value <= max:
        return True, ''
    return False, f"The value needs to be between {min} and {max}"


def environment_list(previous_settings: Dict, current_field: Field) -> Dict:
    """
    Allows the CLI to provide a list of available environments.

    Uses the previous_settings to get the endpoint to query for environments

    Args:
        previous_settings: previous settings set by the user in the CLI.
        current_field: Current field specs

    Returns: updates to the choices and default
    """
    from COMPS import Client
    Client.login(previous_settings["endpoint"])
    client = Client.get("environments")
    environment_choices = []
    for environment_info in client.json()["Environments"]:
        environment_choices.append(environment_info["EnvironmentName"])

    # Set a valid default
    if current_field.default not in environment_choices:
        default_env = environment_choices[0]
    else:
        default_env = current_field.default

    return {"choices": environment_choices, "default": default_env}
