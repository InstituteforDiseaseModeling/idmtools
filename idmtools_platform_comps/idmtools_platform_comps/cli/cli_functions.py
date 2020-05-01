from dataclasses import Field
from typing import Dict


def environment_list(previous_settings:Dict, current_field:Field) -> Dict:
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
