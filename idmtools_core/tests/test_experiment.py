import unittest
from idmtools.builders import SimulationBuilder
from idmtools.core.enums import EntityStatus
from idmtools.entities.experiment import Experiment
from idmtools.entities.simulation import Simulation
from idmtools.entities.templated_simulation import TemplatedSimulations
from idmtools_test.utils.test_task import TestTask

from idmtools_models.python.json_python_task import JSONConfiguredPythonTask
from typing import Dict


class TestAddingSimulationsToExistingExperiment(unittest.TestCase):

    # more detailed than is needed for this test set, but works
    class SetParam:
        def __init__(self, param: str):
            self.param = param

        def __call__(self, simulation: Simulation, value) -> Dict[str, any]:
            return JSONConfiguredPythonTask.set_parameter_sweep_callback(simulation, self.param, value)

    def setUp(self):
        self.experiment = Experiment.from_task(TestTask())

        # no need to actually run the simulations, just mark them done
        self.experiment.simulations.items.set_status(status=EntityStatus.SUCCEEDED)

    def get_new_simulations(self, n=None):
        ts = TemplatedSimulations(base_task=TestTask())
        # create a new sweep for new simulations
        builder = SimulationBuilder()
        builder.add_sweep_definition(self.SetParam("a"), [i * i for i in range(100, 120, 3)])
        ts.add_builder(builder=builder)

        new_simulations = ts if n is None else [simulation for simulation in ts.simulations()][0:n]
        return new_simulations

    def test_adding_simulations_to_experiment_not_done_should_fail(self) -> None:
        new_simulations = self.get_new_simulations(n=1)

        # verify starting case
        self.assertTrue(self.experiment.done)

        # make the experiment 'not done'
        self.experiment.add_new_simulations(simulations=new_simulations)

        self.assertRaises(RuntimeError, self.experiment.add_new_simulations, **{'simulations': [new_simulations]})

    def test_adding_non_builder_simulations_should_work(self) -> None:
        new_simulations = self.get_new_simulations(n=1)

        # add the new simulation and keep track of the existing and total simulation lists
        existing_simulations = [simulation for simulation in self.experiment.simulations.items]
        self.experiment.add_new_simulations(simulations=new_simulations)
        self.verify_added_simulations(experiment=self.experiment, existing_simulations=existing_simulations,
                                      simulations_to_add=new_simulations)

    def test_adding_TemplatedSimulations_should_work(self) -> None:
        new_simulations = self.get_new_simulations()

        # add the new simulations and keep track of the existing and total simulation lists
        existing_simulations = [simulation for simulation in self.experiment.simulations.items]
        simulations_to_add = [simulation for simulation in new_simulations.simulations()]
        self.experiment.add_new_simulations(simulations=new_simulations)

        self.verify_added_simulations(self.experiment, existing_simulations, simulations_to_add)

    def verify_added_simulations(self, experiment, existing_simulations, simulations_to_add):
        # using experiment.simulations.items in here because each iteration over the experiment.simulations object
        # (a ParentIterator) causes all uids to be set to new values...
        all_simulations = [simulation for simulation in experiment.simulations.items]
        existing_uids = [simulation.uid for simulation in existing_simulations]
        added_simulations = [simulation for simulation in all_simulations if simulation.uid not in existing_uids]

        # verify that the correct number of simulations were added
        self.assertEqual(len(existing_simulations) + len(simulations_to_add), len(all_simulations))
        self.assertEqual(len(simulations_to_add), len(added_simulations))

        # verify existing simulations have unchanged status and new simulations are ready to be created by a platform
        for simulation in experiment.simulations.items:
            if simulation.uid in existing_uids:
                self.assertEqual([s for s in existing_simulations if s.uid == simulation.uid][0].status,
                                 simulation.status)
            else:
                self.assertEqual(None, simulation.status)

