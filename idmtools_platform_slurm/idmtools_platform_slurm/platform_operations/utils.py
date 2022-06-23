"""
This is SlurmPlatform operations utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from logging import getLogger, DEBUG
from typing import TYPE_CHECKING, Generator, Dict, Any

logger = getLogger(__name__)


class SuiteDict(dict):
    """Alias for slurm platform experiment objects."""
    pass


class ExperimentDict(dict):
    """Alias for slurm platform experiment objects."""
    pass


class SimulationDict(dict):
    """Alias for slurm platform simulation objects."""
    pass


def clean_experiment_name(experiment_name: str) -> str:
    """
    Handle some special characters in experiment names.
    Args:
        experiment_name: name of the experiment
    Returns:the experiment name allowed for use
    """
    import re
    chars_to_replace = ['/', '\\', ':', "'", '"', '?', '<', '>', '*', '|', "\0", "(", ")", '`']
    clean_names_expr = re.compile(f'[{re.escape("".join(chars_to_replace))}]')

    experiment_name = clean_names_expr.sub("_", experiment_name)
    return experiment_name.encode("ascii", "ignore").decode('utf8').strip()
