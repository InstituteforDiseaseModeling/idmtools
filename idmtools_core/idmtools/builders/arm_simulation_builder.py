"""
idmtools arm builder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import copy
import collections
from enum import Enum
from itertools import product
from typing import Tuple, List, Callable, Iterable, Any

from idmtools.builders import SimulationBuilder


class ArmType(Enum):
    """
    ArmTypes.
    """
    cross = 0
    pair = 1


class SweepArm:
    """
    Class that represents a parameter arm.
    """

    def __init__(self, type=ArmType.cross, funcs: List[Tuple[Callable, Iterable]] = None):
        """
        Constructor.

        Args:
            type: Type of Arm(Cross or Pair)
            funcs: Functions to add as sweeps
        """
        if funcs is None:
            funcs = []
        self.sweep_functions = []
        self.type = type

        for func, values in funcs:
            self.add_sweep_definition(func, values)

    def add_sweep_definition(self, func: Callable, values: Iterable[Any]):  # noqa F821
        """
        Add Sweep definition.

        Args:
            func: Sweep callback
            values: Values to Sweep

        Returns:
            None
        """
        self.sweep_functions.append((func, values if isinstance(values, collections.abc.Iterable) and not (
            isinstance(values, str)) else [values]))

        if self.type == ArmType.pair:
            self.adjust_values_length()

    def get_max_values_count(self):
        """
        Get the max values count from different sweep functions.

        Returns:
            Max values
        """
        cnts = [len(values) for _, values in self.sweep_functions]
        return max(cnts)

    def adjust_values_length(self):
        """
        Adjust values length.

        Returns:
            None
        """
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


class ArmSimulationBuilder(SimulationBuilder):
    """
    Class that represents an experiment builder.

    This particular sweep builder build sweeps in "ARMS". This is particular useful in situations where you want to sweep
    parameters that have branches of parameters. For Example, let's say we have a model with the following parameters:
    * population
    * susceptible
    * recovered
    * enable_births
    * birth_rate

    Enable births controls an optional feature that is controlled by the birth_rate parameter. If we want to sweep a set
    of parameters on population, susceptible with enabled_births set to off but also want to sweep the birth_rate
    we could do that like so

    .. literalinclude:: ../../examples/builders/print_builder_values.py

    This would result in the output

    .. list-table:: Arm Example Values
       :widths: 25 25 25 25
       :header-rows: 1

       * - enable_births
         - population
         - susceptible
         - birth_rate
       * - False
         - 500
         - 0.5
         -
       * - False
         - 500
         - 0.9
         -
       * - False
         - 1000
         - 0.5
         -
       * - False
         - 1000
         - 0.9
         -
       * - True
         - 500
         - 0.5
         - 0.01
       * - True
         - 500
         - 0.5
         - 0.1
       * - True
         - 500
         - 0.9
         - 0.01
       * - True
         - 500
         - 0.9
         - 0.1
       * - True
         - 1000
         - 0.5
         - 0.01
       * - True
         - 1000
         - 0.5
         - 0.1
       * - True
         - 1000
         - 0.9
         - 0.01
       * - True
         - 1000
         - 0.9
         - 0.1

    Examples:
        .. literalinclude:: ../../examples/builders/arm_experiment_builder_python.py
    """

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()
        self.arms = []
        self.sweep_definitions = []

    def add_arm(self, arm):
        """
        Add arm sweep definition.

        Args:
            arm: Arm to add

        Returns:
            None
        """
        arm_list = arm if isinstance(arm, collections.abc.Iterable) else [arm]
        for a in arm_list:
            self.arms.append(a)
            self._apply(a)

    def _apply(self, arm):
        """
        Apply our arm.

        Args:
            arm: Arm to apply

        Returns:
            None
        """
        self.sweeps = []
        for func, values in arm.sweep_functions:
            self.add_sweep_definition(func, values)

        if arm.type == ArmType.cross:
            self.sweep_definitions.extend(product(*self.sweeps))
        elif arm.type == ArmType.pair:
            self.sweep_definitions.extend(zip(*self.sweeps))

    def __iter__(self):
        """
        Iterator for the simulations defined.

        Returns:
            Iterator
        """
        yield from self.sweep_definitions
