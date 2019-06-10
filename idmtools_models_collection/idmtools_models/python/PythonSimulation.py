from idmtools.entities import ISimulation


class PythonSimulation(ISimulation):
    def __init__(self, parameters=None, assets=None):
        super().__init__(parameters, assets)

