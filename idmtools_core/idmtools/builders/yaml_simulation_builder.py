import yaml
from idmtools.builders import ArmSimulationBuilder
from idmtools.builders.arm_simulation_builder import SweepArm, ArmType


class YamlSimulationBuilder(ArmSimulationBuilder):
    """
    Class that represents an experiment builder.

    Examples:
        .. literalinclude:: ../examples/builders/yaml_builder_python.py
    """

    def __init__(self):
        super().__init__()

    def add_sweeps_from_file(self, file_path, func_map={}, sweep_type=ArmType.cross):

        with open(file_path, 'r') as stream:
            try:
                parsed = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                exit()

        d_funcs = parsed.values()

        for sweeps in list(d_funcs):
            sweeps_tuples = ((list(d.keys())[0], list(d.values())[0]) for d in sweeps)
            funcs = []
            for func, values in sweeps_tuples:
                funcs.append((func_map[func], values))

            arm = SweepArm(sweep_type, funcs)
            self.add_arm(arm)

    def __iter__(self):
        for tup in self.sweep_definitions:
            yield tup
