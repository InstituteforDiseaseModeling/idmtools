from typing import List, TypeVar, Dict

from idmtools.analysis import IAnalyzer
from idmtools.entities import CommandLine
from idmtools.builders import ExperimentBuilder

# Base Types

TCommandLine = TypeVar("TCommandLine", bound=CommandLine)
TAnalyzer = TypeVar("TAnalyzer", bound=IAnalyzer)
TExperimentBuilder = TypeVar("TExperimentBuilder", bound=ExperimentBuilder)
TTags = Dict[str, str]

# Analysis types
TAnalyzerList = List[IAnalyzer]
