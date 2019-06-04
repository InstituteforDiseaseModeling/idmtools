from typing import Type, List, Union, TypeVar, Mapping, Any

from idmtools.analysis import IAnalyzer
from idmtools.entities import CommandLine, IPlatform, IExperiment, ISimulation

# Base Types
TExperiment = TypeVar("TExperiment", bound=IExperiment)
TSimulation = TypeVar("TSimulation", bound=ISimulation)
TCommandLine = TypeVar("TCommandLine", bound=CommandLine)
TAnalyzer = TypeVar("TAnalyzer", bound=IAnalyzer)
TPlatform = TypeVar("TPlatform", bound=IPlatform)

TSimulationClass = Type[TSimulation]

# Composed types
TExperimentsList = List[Union[TExperiment, str]]

# Analysis types
TAllSimulationData = Mapping[TSimulation, Any]
TAnalyzerList = List[IAnalyzer]
