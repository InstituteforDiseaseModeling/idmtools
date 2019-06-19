import json
import os
import unittest

from COMPS import Data
from COMPS.Data import Experiment, QueryCriteria, Simulation

from idmtools.assets import Asset, AssetCollection
from idmtools.builders import ExperimentBuilder
from idmtools.core import EntityStatus
from idmtools.platforms import COMPSPlatform
from idmtools_models.python import PythonExperiment
from tests import INPUT_PATH
from tests.utils.decorators import comps_test


@comps_test
class TestAssetsInComps(unittest.TestCase):

    def setUp(self) -> None:
        self.base_path = os.path.abspath(os.path.join(INPUT_PATH, "assets", "collections"))
        self.platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")
        self.casename = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.casename)

        def setP(simulation, p):
            return simulation.set_parameter("P", p)

        self.builder = ExperimentBuilder()
        self.builder.add_sweep_definition(setP, [1, 2, 3])

    def _run_and_test_experiment(self, experiment):
        experiment.builder = self.builder

        # Create experiment on platform
        experiment.pre_creation()
        self.platform.create_experiment(experiment)

        for simulation_batch in experiment.batch_simulations(batch_size=10):
            # Create the simulations on the platform
            for simulation in simulation_batch:
                simulation.pre_creation()

            ids = self.platform.create_simulations(simulation_batch)

            for uid, simulation in zip(ids, simulation_batch):
                simulation.uid = uid
                simulation.post_creation()

                from idmtools.entities import ISimulation
                simulation.__class__ = ISimulation
                experiment.simulations.append(simulation)

        self.platform.refresh_experiment_status(experiment)

        # Test if we have all simulations at status CREATED
        self.assertFalse(experiment.done)
        self.assertTrue(all([s.status == EntityStatus.CREATED for s in experiment.simulations]))

        # Start experiment
        self.platform.run_simulations(experiment)
        self.platform.refresh_experiment_status(experiment)
        self.assertFalse(experiment.done)
        self.assertTrue(all([s.status == EntityStatus.RUNNING for s in experiment.simulations]))

        # Wait till done
        import time
        start_time = time.time()
        while time.time() - start_time < 180:
            self.platform.refresh_experiment_status(experiment)
            if experiment.done:
                break
            time.sleep(3)
        self.assertTrue(experiment.done)

    def test_md5hashing_for_same_files_content(self):
        a = Asset(relative_path=None, filename="test.json", content=json.dumps({"a": 1, "b": 2}))
        b = Asset(relative_path=None, filename="test1.json", content=json.dumps({"a": 1, "b": 2}))

        ac = AssetCollection()
        ac.add_asset(a)
        ac.add_asset(b)

        pe = PythonExperiment(name=self.casename,
                                      model_path=os.path.join(INPUT_PATH, "compsplatform", "working_model.py"), assets=ac)
        pe.tags = {"idmtools": "idmtools-automation"}
        self._run_and_test_experiment(pe)
        exp_id = pe.uid
        #exp_id = 'ae077ddd-668d-e911-a2bb-f0921c167866'
        for simulation in Experiment.get(exp_id).get_simulations():
            collection_id = self.get_asset_collection_id_for_simulation_id(simulation.id)
            asset_collection = self.get_asset_collection_by_id(collection_id)
            self.assertEqual(asset_collection.assets[0]._md5_checksum, asset_collection.assets[1]._md5_checksum)
            self.assertEqual(asset_collection.assets[0]._file_name,'test.json')
            self.assertEqual(asset_collection.assets[1]._file_name,'test1.json')

    def get_asset_collection_id_for_simulation_id(self, sim_id):
        query_criteria = QueryCriteria().select_children('configuration')
        simulation = Simulation.get(id=sim_id, query_criteria=query_criteria)
        collection_id = simulation.configuration.asset_collection_id
        return collection_id

    def get_asset_collection_by_id(self, collection_id, query_criteria=None):
        query_criteria = query_criteria or QueryCriteria().select_children('assets')
        try:
            return Data.AssetCollection.get(collection_id, query_criteria)
        except (RuntimeError, ValueError):
            return None

if __name__ == '__main__':
    unittest.main()