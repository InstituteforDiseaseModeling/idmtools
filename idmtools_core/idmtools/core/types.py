from typing import List, TypeVar, Dict

from idmtools.builders import ExperimentBuilder

# Base Types

TExperimentBuilder = TypeVar("TExperimentBuilder", bound=ExperimentBuilder)
TTags = Dict[str, str]
