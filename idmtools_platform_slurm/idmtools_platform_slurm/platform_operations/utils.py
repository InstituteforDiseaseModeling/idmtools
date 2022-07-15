"""
This is SlurmPlatform operations utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from typing import Dict
from idmtools.core import ItemType
from idmtools.entities import Suite
from idmtools.entities.experiment import Experiment
from logging import getLogger

logger = getLogger(__name__)


class SlurmSuite:
    def __init__(self, kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if hasattr(self, 'item_type'):
            setattr(self, 'item_type', ItemType[getattr(self, 'item_type').upper()])


class SlurmExperiment:
    def __init__(self, kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if hasattr(self, 'item_type'):
            setattr(self, 'item_type', ItemType[getattr(self, 'item_type').upper()])


class SlurmSimulation:
    def __init__(self, kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if hasattr(self, 'item_type'):
            setattr(self, 'item_type', ItemType[getattr(self, 'item_type').upper()])


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


def add_dammy_suite(experiment: Experiment, suite_name: str = None, tags: Dict = None) -> Suite:
    """
    Create Suite parent for given experiment
    Args:
        experiment: idmtools Experiment
        suite_name: new Suite name
        tags: new Suite tags
    Returns:

    """
    if suite_name is None:
        suite_name = 'Dammy Suite'
    suite = Suite(name=suite_name)

    if not tags:
        suite.tags = tags

    # add experiment
    suite.add_experiment(experiment)

    return suite
