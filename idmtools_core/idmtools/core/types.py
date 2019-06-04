from typing import Any, Callable, List, Mapping, Type, TypeVar, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from idmtools.analysis import IAnalyzer
    from idmtools.entities import CommandLine, IExperiment, IPlatform, ISimulation
    from idmtools.assets import Asset, AssetCollection

    # Base Types
    TExperiment = TypeVar("TExperiment", bound=IExperiment)
    TSimulation = TypeVar("TSimulation", bound=ISimulation)
    TCommandLine = TypeVar("TCommandLine", bound=CommandLine)
    TAnalyzer = TypeVar("TAnalyzer", bound=IAnalyzer)
    TPlatform = TypeVar("TPlatform", bound=IPlatform)
    TAssetCollection = TypeVar("TAssetCollection", bound=AssetCollection)
    TAsset = TypeVar("TAsset", bound=Asset)

    TSimulationClass = Type[TSimulation]

    # Composed types
    TExperimentsList = List[Union[TExperiment, str]]

    # Analysis types
    TAllSimulationData = Mapping[TSimulation, Any]
    TAnalyzerList = List[IAnalyzer]

    # Assets types
    TAssetList = List[TAsset]

    # Filters types
    TAssetFilter = Callable[[TAsset], bool]
    TAssetFilterList = List[TAssetFilter]
