from typing import List

from idmtools.workflows.calibration import Parameter


class Sample:
    def __init__(self, index: int, parameters: List[Parameter]=None):
        self.parameters = parameters or []
        self.index = index

    def __repr__(self):
        params = " ".join([f"{p.name}={p.value}" for p in self.parameters])
        return f"<Sample #{self.index} {params}>"

    def __iter__(self):
        yield from self.parameters
