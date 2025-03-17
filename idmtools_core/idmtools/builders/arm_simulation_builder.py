"""
idmtools arm builder definition.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
from idmtools.builders import SweepArm
from itertools import tee


class ArmSimulationBuilder:
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

    @property
    def count(self):
        """
        Total simulations to be built by builder.
        Returns:
            arm count
        """
        return sum([arm.count for arm in self.arms])

    def add_arm(self, arm):
        """
        Add arm sweep definition.
        Args:
            arm: Arm to add
        Returns:
            None
        """
        # create a new arm
        arm_new = SweepArm(type=arm.type)
        old_sweeps = []
        new_sweeps = []
        # make two copies of each sweep
        for sweep in arm.sweeps:
            old_sw, new_sw = tee(sweep, 2)
            old_sweeps.append(old_sw)
            new_sweeps.append(new_sw)

        # keep original sweeps
        arm.sweeps = old_sweeps
        # copy sweeps to new arm
        arm_new.sweeps = new_sweeps
        # update count for new arm
        arm_new.count = arm.count

        # add new arm to arms
        self.arms.append(arm_new)
        # update sweep functions for new arm
        arm_new._update_sweep_functions()

    def __iter__(self):
        """
        Iterator for the simulations defined.
        Returns:
            Iterator
        """
        for arm in self.arms:
            yield from arm.functions

    def __len__(self):
        """
        Total simulations to be built by builder.
        Returns:
            Simulation count
        """
        return self.count
