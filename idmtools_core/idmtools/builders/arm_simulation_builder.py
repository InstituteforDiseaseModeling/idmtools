"""
idmtools arm builder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from enum import Enum
from itertools import product
from typing import Tuple, List, Callable, Iterable
from idmtools.builders import SimulationBuilder
from idmtools.builders.simulation_builder import TSweepFunction


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
        self.type = type
        self.sweeps = []
        self.__count = 0

        if funcs is None:
            funcs = []
        for func, values in funcs:
            self.add_sweep_definition(func, values)

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, cnt):
        """
        Set the count property.
        Args:
            cnt: count set
        Returns:
            int
        """
        # print('cnt: ', cnt)
        if self.__count == 0:
            self.__count = cnt
        elif self.type == ArmType.cross:
            self.__count = self.__count * cnt
        elif self.type == ArmType.pair:
            if self.__count != cnt:
                raise ValueError(
                    f"For pair case, all function inputs must have the save size/length: {cnt} != {self.__count}")
            else:
                self.__count = cnt

    def add_sweep_definition(self, function: TSweepFunction, values):
        """
        Add a parameter sweep definition.

        A sweep definition is composed of a function and a list of values to call the function with.

        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
                The function also must include EXACTLY ONE free parameter, which the values will be passed to.
                The function can also be a partial--any Callable type will work.
            values: The list of values to call the function with.

        Examples:
            Examples of valid function::

                def myFunction(simulation, parameter):
                    pass

            How to deal with functions requiring more than one parameter?
            Consider the following function::

                python
                def myFunction(simulation, a, b):
                    pass

            Partial solution::

                python
                from functools import partial
                func = partial(myFunction, a=3)
                eb.add_sweep_definition(func, [1,2,3])

            Callable class solution::

                class setP:
                    def __init__(self, a):
                        self.a = a

                    def __call__(self, simulation, b):
                        return param_update(simulation, self.a, b)

                eb.add_sweep_definition(setP(3), [1,2,3])
        """
        builder = SimulationBuilder()
        builder.add_sweep_definition(function, values)
        self.sweeps.extend(builder.sweeps)
        self.count = builder.count

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes multiple parameters.

        The sweep will be defined as a cross-product between the parameters passed.

        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
            args: List of arguments to be passed
            kwargs: List of keyword arguments to be passed

        Returns:
            None. Updates the Sweeps

        Examples:
            Examples of valid functions::

                # This function takes two parameters
                def myFunction(simulation, parameter_a, parameter_b):
                    pass

                # Function that takes three parameters
                def three_param_callback(simulation, parameter_a, parameter_b, parameter_c):
                    pass

            Calling Sweeps that take multiple parameters::

                # This example references the above valid function example
                sb = SimulationBuilder()

                # Add a sweep on the myFunction that takes two parameters.
                # Here we sweep the values 1-4 on parameter_a and a,b on parameter_b
                sb.add_multiple_parameter_sweep_definition(myFunction, range(1,5), ["a", "b"])

                sb2 = SimulationBuilder()
                # Example calling using a dictionary instead
                sb.add_multiple_parameter_sweep_definition(three_param_callback, dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))
                # The following is equivalent
                sb.add_multiple_parameter_sweep_definition(three_param_callback, **dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))

        """
        builder = SimulationBuilder()
        builder.add_multiple_parameter_sweep_definition(function, *args, **kwargs)
        self.sweeps.extend(builder.sweeps)
        self.count = builder.count


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

    def add_arm(self, arm: ArmType):
        """
        Add arm sweep definition.
        Args:
            arm: Arm to add
        Returns:
            None
        """
        self.arms.append(arm)
        if arm.type == ArmType.cross:
            self.sweep_definitions.extend(product(*arm.sweeps))
        elif arm.type == ArmType.pair:
            self.sweep_definitions.extend(zip(*arm.sweeps))
        self.count = sum([arm.count for arm in self.arms])

    def add_sweep_definition(self, function: TSweepFunction, values):
        raise ValueError(f"Please use SweepArm instead, or use SimulationBuilder directly!")

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        raise ValueError(f"Please use SweepArm instead, or use SimulationBuilder directly!")

    def __iter__(self):
        """
        Iterator for the simulations defined.
        Returns:
            Iterator
        """
        yield from self.sweep_definitions
