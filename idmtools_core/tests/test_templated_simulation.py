from unittest import TestCase
import pytest
from idmtools.builders import SimulationBuilder
from idmtools.entities.command_task import CommandTask

from idmtools.entities.templated_simulation import TemplatedSimulations


def print_sweep(simulation, value):
    print(value)
    return dict()


@pytest.mark.tasks
class TestTemplatedSimulation(TestCase):
    def test_generator(self):
        ts = TemplatedSimulations(base_task=CommandTask(command='ls'))
        builder = SimulationBuilder()
        total = 10
        builder.add_sweep_definition(print_sweep, range(total))
        ts.add_builder(builder)
        sims = [s for s in ts.simulations()]
        self.assertEqual(len(sims), total)
