from typing import List, TypeVar, Dict

from idmtools.entities import CommandLine
from idmtools.builders import ExperimentBuilder

# Base Types

TCommandLine = TypeVar("TCommandLine", bound=CommandLine)
TExperimentBuilder = TypeVar("TExperimentBuilder", bound=ExperimentBuilder)
TTags = Dict[str, str]
