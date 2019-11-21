from dataclasses import dataclass
from idmtools.entities.experiment import Experiment


@dataclass(repr=False)
class TstExperiment(Experiment):
    def __post_init__(self, model_type):
        super().__post_init__(model_type=model_type)

    def gather_assets(self) -> None:
        pass
