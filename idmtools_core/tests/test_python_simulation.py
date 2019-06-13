import os
import unittest
from functools import partial
from operator import itemgetter

from COMPS.Data import Experiment, QueryCriteria

from idmtools.builders import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools.platforms import COMPSPlatform
from idmtools_models.python.PythonExperiment import PythonExperiment
from tests import INPUT_PATH
from tests.utils.decorators import comps_test
from tests.utils.ITestWithPersistence import ITestWithPersistence


class TestPythonSimulation(ITestWithPersistence):

    def test_retrieve_extra_libraries(self):
        ps = PythonExperiment(name="Test experiment", model_path=os.path.join(INPUT_PATH, "python", "model.py"))
        self.assertTrue("numpy" in ps.retrieve_python_dependencies()[0])

    # Test 2 ways to sweep parameters
    # First way: use partial function
    # Second way: define a setParam class and __call__ method
    # Also current add_sweep_definition will do product of each call. if first call has 5 parameters, second call also
    # has 5 parameter, total sweep parameters are 5*5=25
    @comps_test
    def test_python_model_in_comps_sweeps_with_partial(self):
        self.platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")
        name = "Test python experiment"
        experiment = PythonExperiment(name=name,
                                      model_path=os.path.join(INPUT_PATH, "python", "model1.py"))
        experiment.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        experiment.base_simulation.set_parameter("c", "c-value")

        def param_update(simulation, param, value):
            return simulation.set_parameter(param, value)

        setA = partial(param_update, param="a")

        class setParam:
            def __init__(self, param):
                self.param = param

            def __call__(self, simulation, value):
                return param_update(simulation, self.param, value)

        builder = ExperimentBuilder()

        # ------------------------------------------------------
        # Sweeping parameters:
        # first way to sweep parameter 'a' is to use param_update function
        builder.add_sweep_definition(setA, range(0, 2))

        # second way to sweep parameter 'b' is to use class setParam which basiclly doing same thing as param_update mathod
        builder.add_sweep_definition(setParam("b"), [i * i for i in range(1, 4, 2)])
        # ------------------------------------------------------

        experiment.builder = builder

        em = ExperimentManager(experiment=experiment, platform=self.platform)
        em.run()
        em.wait_till_done()
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        exp_id = experiment.id
        # exp_id = "a727e802-d88b-e911-a2bb-f0921c167866"

        # validation each simulation output to compare output/config.json is equal to config.json
        self.validate_output(exp_id, 4)

        expected_tags = [{'a': '0', 'b': '1'}, {'a': '0', 'b': '9'}, {'a': '1', 'b': '1'}, {'a': '1', 'b': '9'}]
        self.validate_sim_tags(exp_id, expected_tags)

        # validate experiment tags
        exp_tags = experiment.get(experiment.id, QueryCriteria().select_children('tags')).tags
        self.assertEqual({'idmtools': 'idmtools-automation', 'number_tag': '123', 'string_tag': 'test'}, exp_tags)

    # Test parameter "b" set is depending on parameter "a"
    # a=[0,1,2,3,4] <--sweep parameter
    # b=[2,3,4,5,6]  <-- b = a + 2
    @comps_test
    def test_python_model_in_comps_sweeps_2_related_parameters(self):
        self.platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")
        name = "Test python experiment"
        experiment = PythonExperiment(name=name,
                                      model_path=os.path.join(INPUT_PATH, "python", "model1.py"))
        experiment.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        experiment.base_simulation.set_parameter("c", "c-value")

        def param_update(simulation, param, value):
            # Set B within
            if param == "a":
                simulation.set_parameter("b", value + 2)

            return simulation.set_parameter(param, value)

        setAB = partial(param_update, param="a")

        builder = ExperimentBuilder()
        # Sweep parameter "a" and make "b" depends on "a"
        builder.add_sweep_definition(setAB, range(0, 5))
        experiment.builder = builder
        em = ExperimentManager(experiment=experiment, platform=self.platform)
        em.run()
        em.wait_till_done()
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        exp_id = experiment.id
        self.validate_output(exp_id, 5)

        # validate b is not in tag since it is not sweep parameter, it just depend on sweep parameter
        expected_tags = [{'a': '0'}, {'a': '1'}, {'a': '2'}, {'a': '3'}, {'a': '4'}]
        self.validate_sim_tags(exp_id, expected_tags)

    @comps_test
    def test_python_model_in_comps_direct_sweep_one_paramater(self):
        self.platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")
        name = "Test python experiment"
        experiment = PythonExperiment(name=name,
                                      model_path=os.path.join(INPUT_PATH, "python", "model1.py"))
        experiment.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        # Sweep parameter "a"
        builder.add_sweep_definition(param_a_update, range(0, 5))
        experiment.builder = builder
        em = ExperimentManager(experiment=experiment, platform=self.platform)
        em.run()
        em.wait_till_done()
        experiment = Experiment.get(em.experiment.uid)
        print(experiment.id)
        exp_id = experiment.id
        self.validate_output(exp_id, 5)

        # validate b is not in tag since it is not sweep parameter, it just depend on sweep parameter
        expected_tags = [{'a': '0'}, {'a': '1'}, {'a': '2'}, {'a': '3'}, {'a': '4'}]
        self.validate_sim_tags(exp_id, expected_tags)

    # sweep in arms:
    # |__ P1 = 1
    #      |_ P2 = [2,3]
    #      |_ P3 = [4,5]
    # |__ P1 = [6,7]
    #    |_ P2 = 2
    def test_python_model_in_comps_sweep_In_arms(self):
        print("TODO")

    @comps_test
    def test_duplicate_asset_file_not_allowed(self):
        self.platform = COMPSPlatform(endpoint="https://comps2.idmod.org", environment="Bayesian")
        name = "Test dup files -experiment"
        experiment = PythonExperiment(name=name,
                                      model_path=os.path.join(INPUT_PATH, "python", "model1.py"))
        experiment.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}
        experiment.assets.add_directory(
            assets_directory=os.path.join(INPUT_PATH, "python", "folder_dup_file"))
        builder = ExperimentBuilder()
        experiment.builder = builder
        em = ExperimentManager(experiment=experiment, platform=self.platform)
        with self.assertRaises(RuntimeError) as context:
            em.run()
        self.assertTrue(
            "400 Bad Request - An error was encountered while attempting to save asset collection: Cannot insert " \
            "duplicate key row in object 'dbo.AssetCollectionFile' with unique index " \
            "'IX_AssetCollectionFile_AssetCollectionId_NewFileName_RelativePath_Unique'." in str(
                context.exception.args[0]))

    def validate_output(self, exp_id, expected_sim_count):
        sim_count = 0
        for simulation in Experiment.get(exp_id).get_simulations():
            sim_count = sim_count + 1
            resultFileString = simulation.retrieve_output_files(paths=['output/result.json'])
            print(resultFileString)
            configString = simulation.retrieve_output_files(paths=['config.json'])
            print(configString)
            self.assertEqual(resultFileString, configString)

        self.assertEqual(sim_count, expected_sim_count)

    def validate_sim_tags(self, exp_id, expected_tags):
        tags = []
        for simulation in Experiment.get(exp_id).get_simulations():
            tags.append(simulation.get(simulation.id, QueryCriteria().select_children('tags')).tags)

        sorted_tags = sorted(tags, key=itemgetter('a'))
        sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
        self.assertEqual(sorted_tags, sorted_expected_tags)


if __name__ == '__main__':
    unittest.main()
