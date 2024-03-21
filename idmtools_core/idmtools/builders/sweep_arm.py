"""
idmtools SimulationBuilder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from enum import Enum
from functools import partial
from itertools import product, tee
from typing import Callable, Any, Iterable, Union, List, Tuple, Dict
from idmtools.builders import SimulationBuilder
from idmtools.entities.simulation import Simulation

TSweepFunction = Union[
    Callable[[Simulation, Any], Dict[str, Any]], partial
]


class ArmType(Enum):
    """
    ArmTypes.
    """
    cross = 0
    pair = 1


class SweepArm(SimulationBuilder):
    """
    Class that represents a section of simulation sweeping.
    """

    def __init__(self, type=ArmType.cross, funcs: List[Tuple[Callable, Iterable]] = None):
        """
        Constructor.
        """
        self.type = type
        self.__count = 0
        self.__functions = None
        super().__init__()

        if funcs is None:
            funcs = []
        for func, values in funcs:
            self.add_sweep_definition(func, values)

    @property
    def count(self):
        """return simulations count."""
        return self.__count

    @count.setter
    def count(self, cnt):
        """
        Set simulations count.
        Args:
            cnt: count to set
        Returns:
            None
        """
        if self.__count == 0:
            self.__count = cnt
        elif self.type == ArmType.cross:
            self.__count = self.__count * cnt
        elif self.type == ArmType.pair:
            if self.__count != cnt:
                raise ValueError(f"For pair case, all function inputs must have the same size/length: {cnt} != {self.__count}")
            else:
                self.__count = cnt

    @property
    def functions(self):
        old_sw, new_sw = tee(self.__functions, 2)
        self.__functions = new_sw
        return old_sw

    @functions.setter
    def functions(self, funcs):
        self.__functions = funcs

    def _update_sweep_functions(self):
        result = []
        if len(self.sweeps) == 0:
            result = []
        elif self.type == ArmType.cross:
            result = product(*self.sweeps)
        elif self.type == ArmType.pair:
            result = zip(*self.sweeps)

        self.__functions = result

    def _update_count(self, values):
        """
        Update count of sweeps.
        Args:
            values: Values to count
        Returns:
            None
        """
        if self.count == 0:
            if len(values) == 0:
                self.count = 1
            else:
                self.count = len(values)
        else:
            self.count = len(values)
