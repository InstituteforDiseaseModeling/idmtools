"""
idmtools YamlSimulationBuilder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import yaml
from logging import getLogger
from typing import Union, Callable, Dict, Any
from idmtools.builders import ArmSimulationBuilder, SweepArm

logger = getLogger(__name__)


class DefaultParamFuncDict(dict):
    """
    Enables a function that takes a single parameter and return another function.

    Notes:
        TODO Add Example and types
    """

    def __init__(self, default):
        """
        Initialize our DefaultParamFuncDict.
        Args:
            default: Default function to use
        """
        super().__init__()
        self.__default = default

    def __getitem__(self, item):
        """
        Get item from the DefaultParamFuncDict. It proxies most calls to the function we wrap.
        Args:
            item: Item to lookup
        Returns:
            None
        """
        if item in self:
            return super().__getitem__(item)
        else:
            return self.__default(item)


class YamlSimulationBuilder(ArmSimulationBuilder):
    """
    Class that represents an experiment builder.
    Examples:
        .. literalinclude:: ../../examples/builders/yaml_builder_python.py
    """

    def add_sweeps_from_file(self, file_path, func_map: Union[Dict[str, Callable], Callable[[Any], Dict]] = None):
        """
        Add sweeps from a file.
        Args:
            file_path: Path to file
            func_map: Optional function map
        Returns:
            None
        """
        if func_map is None:
            func_map = {}
        # if the user passing a single function, map it to all values
        elif callable(func_map):
            func_map = DefaultParamFuncDict(func_map)
        with open(file_path, 'r') as stream:
            try:
                parsed = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                logger.exception(exc)
                exit()

        d_funcs = parsed.values()

        for sweeps in list(d_funcs):
            sweeps_tuples = ((list(d.keys())[0], list(d.values())[0]) for d in sweeps)
            funcs = []
            for func, values in sweeps_tuples:
                funcs.append((func_map[func], values))

            arm = SweepArm(funcs=funcs)
            self.add_arm(arm)
