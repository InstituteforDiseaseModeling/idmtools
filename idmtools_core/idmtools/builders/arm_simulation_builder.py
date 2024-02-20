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
    def count(self) -> int:
        """
        Simulation count.
        Returns:
            count
        """
        return self.__count

    @count.setter
    def count(self, cnt: int):
        """
        Set the count property.
        Args:
            cnt: count set
        Returns:
            None
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

    def add_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes possible multiple parameters (None or many).

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

                # This function takes one parameter
                def myFunction(simulation, parameter_a):
                    pass

               # This function takes one parameter with default value
                def myFunction(simulation, parameter_a=6):
                    pass

                # This function takes two parameters (parameters may have default values)
                def myFunction(simulation, parameter_a, parameter_b=9):
                    pass

                # Function that takes three parameters (parameters may have default values)
                def three_param_callback(simulation, parameter_a, parameter_b, parameter_c=10):
                    pass

            Calling Sweeps that take multiple parameters::

                # This example references the above valid function example
                sb = SimulationBuilder()

                # Add a sweep on the myFunction that takes parameter(s).
                # Here we sweep the values 1-4 on parameter_a and a,b on parameter_b
                sb.add_sweep_definition(myFunction, range(1,5), ["a", "b"])

                sb2 = SimulationBuilder()
                # Example calling using a dictionary instead
                sb.add_sweep_definition(three_param_callback, dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))
                # The following is equivalent
                sb.add_sweep_definition(three_param_callback, **dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))

                sb3 = SimulationBuilder()
                # If all parameters have default values, we can even simply do
                sb3.add_sweep_definition(three_param_callback)


            Remark: in general
                def my_callback(simulation, parameter_1, parameter_2, ..., parameter_n):
                    pass

                Calling Sweeps that take multiple parameters::

                sb = SimulationBuilder()
                sb.add_sweep_definition(my_callback, Iterable_1, Iterable_2, ..., Iterable_m)

                Note:   the # of Iterable object must match the parameters # of my_callback, which don't have default values

                Or use the key (parameter names)

                sb = SimulationBuilder()
                sb.add_sweep_definition(my_callback, parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m)
                # The following is equivalent
                sb.add_sweep_definition(my_callback, dict(parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m))
                and
                sb.add_sweep_definition(my_callback, **dict(parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m))
        """
        builder = SimulationBuilder()
        builder.add_sweep_definition(function, *args, **kwargs)
        self.sweeps.extend(builder.sweeps)
        self.count = builder.count

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add a sweep definition callback that takes possible multiple parameters (None or many).

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

                # This function takes one parameter
                def myFunction(simulation, parameter_a):
                    pass

               # This function takes one parameter with default value
                def myFunction(simulation, parameter_a=6):
                    pass

                # This function takes two parameters (parameters may have default values)
                def myFunction(simulation, parameter_a, parameter_b=9):
                    pass

                # Function that takes three parameters (parameters may have default values)
                def three_param_callback(simulation, parameter_a, parameter_b, parameter_c=10):
                    pass

            Calling Sweeps that take multiple parameters::

                # This example references the above valid function example
                sb = SimulationBuilder()

                # Add a sweep on the myFunction that takes parameter(s).
                # Here we sweep the values 1-4 on parameter_a and a,b on parameter_b
                sb.add_sweep_definition(myFunction, range(1,5), ["a", "b"])

                sb2 = SimulationBuilder()
                # Example calling using a dictionary instead
                sb.add_sweep_definition(three_param_callback, dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))
                # The following is equivalent
                sb.add_sweep_definition(three_param_callback, **dict(parameter_a=range(1,5), parameter_b=["a", "b"], parameter_c=range(4,5))

                sb3 = SimulationBuilder()
                # If all parameters have default values, we can even simply do
                sb3.add_sweep_definition(three_param_callback)


            Remark: in general
                def my_callback(simulation, parameter_1, parameter_2, ..., parameter_n):
                    pass

                Calling Sweeps that take multiple parameters::

                sb = SimulationBuilder()
                sb.add_sweep_definition(my_callback, Iterable_1, Iterable_2, ..., Iterable_m)

                Note:   the # of Iterable object must match the parameters # of my_callback, which don't have default values

                Or use the key (parameter names)

                sb = SimulationBuilder()
                sb.add_sweep_definition(my_callback, parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m)
                # The following is equivalent
                sb.add_sweep_definition(my_callback, dict(parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m))
                and
                sb.add_sweep_definition(my_callback, **dict(parameter_1=Iterable_1, parameter_2=Iterable_2, ..., parameter_m=Iterable_m))
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

    def add_arm(self, arm: SweepArm):
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

    def add_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add parameters sweep definition.
        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
                The function also must include EXACTLY ONE free parameter, which the values will be passed to.
                The function can also be a partial--any Callable type will work.
            args: List of arguments to be passed
            kwargs: List of keyword arguments to be passed
        Returns:
            None
        """
        raise ValueError("Please use SweepArm instead, or use SimulationBuilder directly!")

    def add_multiple_parameter_sweep_definition(self, function: TSweepFunction, *args, **kwargs):
        """
        Add parameters sweep definition.
        Args:
            function: The sweep function, which must include a **simulation** parameter (or
                whatever is specified in :attr:`~idmtools.builders.ExperimentBuilder.SIMULATION_ATTR`).
                The function also must include EXACTLY ONE free parameter, which the values will be passed to.
                The function can also be a partial--any Callable type will work.
            args: List of arguments to be passed
            kwargs: List of keyword arguments to be passed
        Returns:
            None
        """
        raise ValueError("Please use SweepArm instead, or use SimulationBuilder directly!")

    def __iter__(self):
        """
        Iterator for the simulations defined.
        Returns:
            Iterator
        """
        yield from self.sweep_definitions
