from idmtools.entities import ISimulation


class TestSimulation(ISimulation):
    def set_parameter(self, name: str, value: any) -> dict:
        pass

    def gather_assets(self) -> None:
        pass