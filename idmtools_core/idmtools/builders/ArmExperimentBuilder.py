import copy
import collections
from enum import Enum
from itertools import product
from idmtools.builders import ExperimentBuilder


class ArmType(Enum):
    cross = 0
    pair = 1


class SweepArm:
    """
    Represents a parameter arm.
    """

    def __init__(self, type=ArmType.cross, funcs=[]):
        self.sweep_functions = []
        self.type = type

        for func, values in funcs:
            self.add_sweep_definition(func, values)

    def add_sweep_definition(self, func: 'Callable', values: 'Iterable[Any]'):  # noqa F821
        self.sweep_functions.append((func, values if isinstance(values, collections.abc.Iterable) else [values]))

        if self.type == ArmType.pair:
            self.adjust_values_length()

    def get_max_values_count(self):
        cnts = [len(values) for _, values in self.sweep_functions]
        return max(cnts)

    def adjust_values_length(self):
        if self.type != ArmType.pair:
            return

        count_max = self.get_max_values_count()
        temp_sweep_functions = []
        for func, values in self.sweep_functions:
            values_new = copy.deepcopy(values)
            values_new = list(values_new)
            values_new.extend([values[-1]] * (count_max - len(values)))
            temp_sweep_functions.append((func, values_new))

        self.sweep_functions = temp_sweep_functions


class ArmExperimentBuilder(ExperimentBuilder):
    """
    Represents an experiment builder.
    """

    def __init__(self):
        super().__init__()
        self.arms = []
        self.sweep_definitions = []

    def add_arm(self, arm):
        arm_list = arm if isinstance(arm, collections.abc.Iterable) else [arm]
        for a in arm_list:
            self.arms.append(a)
            self._apply(a)

    def _apply(self, arm):
        self.sweeps = []
        for func, values in arm.sweep_functions:
            self.add_sweep_definition(func, values)

        if arm.type == ArmType.cross:
            self.sweep_definitions.extend(product(*self.sweeps))
        elif arm.type == ArmType.pair:
            self.sweep_definitions.extend(zip(*self.sweeps))

    def __iter__(self):
        for tup in self.sweep_definitions:
            yield tup
