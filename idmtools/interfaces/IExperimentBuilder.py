import inspect
from abc import ABCMeta
from functools import partial
from inspect import signature
from itertools import product


class IExperimentBuilder(metaclass=ABCMeta):
    """
    Represents an experiment builder
    """
    SIMULATION_ATTR = 'simulation'

    def __init__(self):
        self.sweeps = []

    def add_sweep_definition(self, function, values):
        parameters = signature(function).parameters

        if self.SIMULATION_ATTR not in parameters:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to take a {self.SIMULATION_ATTR} argument!")

        remaining_parameters = [name for name, param in parameters.items() if
                                name != self.SIMULATION_ATTR and param.default == inspect.Parameter.empty]

        if len(remaining_parameters) > 1:
            raise ValueError(f"The function {function} passed to SweepBuilder.add_sweep_definition "
                             f"needs to only have {self.SIMULATION_ATTR} and exactly one free parameter.")

        self.sweeps.append((partial(function, **{remaining_parameters[0]: v})) for v in values)

    def __iter__(self):
        for tup in product(*self.sweeps):
            yield tup
