import json
import os
import re
import subprocess
import unittest
from operator import itemgetter

from idmtools.builders import ExperimentBuilder
from idmtools.managers import ExperimentManager
from idmtools_platform_local.local_platform import LocalPlatform
from idmtools_platform_local.client.experiments_client import ExperimentsClient
from idmtools_platform_local.client.simulations_client import SimulationsClient
from idmtools_models.python import PythonExperiment
from idmtools_test.utils.ITestWithPersistence import ITestWithPersistence
from idmtools_test import COMMON_INPUT_PATH


class TestLocalRunnerCLI(ITestWithPersistence):

    @classmethod
    def setUpClass(cls):
        platform = LocalPlatform()
        cls.pe = PythonExperiment(name="python experiment", model_path=os.path.join(COMMON_INPUT_PATH, "python", "model1.py"))

        cls.pe.tags = {"idmtools": "idmtools-automation", "string_tag": "test", "number_tag": 123}

        def param_a_update(simulation, value):
            simulation.set_parameter("a", value)
            return {"a": value}

        builder = ExperimentBuilder()
        builder.add_sweep_definition(param_a_update, range(0, 5))
        cls.pe.builder = builder

        em = ExperimentManager(experiment=cls.pe, platform=platform)
        em.run()
        em.wait_till_done()

    def setUp(self) -> None:
        self.case_name = os.path.basename(__file__) + "--" + self._testMethodName
        print(self.case_name)

    def test_status_experimentClient_api(self):
        # Test 1: get_all experiments with experiment id and tags
        experiment = ExperimentsClient.get_all(str(self.pe.uid),
                                               tags=[('idmtools', 'idmtools-automation'), ('string_tag', 'test')])
        self.assertEqual(experiment[0]['experiment_id'], str(self.pe.uid))
        self.assertEqual(experiment[0]['tags'], self.pe.tags)
        self.assertEqual(experiment[0]['data_path'], '/data/' + str(self.pe.uid))
        self.assertEqual(experiment[0]['extra_details'], {'simulation_type': None})

        # Test 2: get_one experiment with experiment id and tags
        experiment1 = ExperimentsClient.get_one(str(self.pe.uid),
                                                tags=[('idmtools', 'idmtools-automation'), ('string_tag', 'test')])

        self.assertEqual(experiment1['experiment_id'], str(self.pe.uid))
        self.assertEqual(experiment1['tags'], self.pe.tags)
        self.assertEqual(experiment1['data_path'], '/data/' + str(self.pe.uid))
        self.assertEqual(experiment1['extra_details'], {'simulation_type': None})

    def test_status_simulationClient_api(self):
        # Test 1: get_all simulations with simulation id only filter
        for s in self.pe.simulations:
            simulations = SimulationsClient.get_all(str(s.uid))
            self.assertEqual(simulations[0]['simulation_uid'], str(s.uid))
            self.assertEqual(simulations[0]['experiment_id'], str(self.pe.uid))
            print(simulations[0]['status'])
            # self.assertEqual(simulations[0]['status'], s.status.value) # wait for bug fix
            self.assertEqual(simulations[0]['tags'], s.tags)
            self.assertEqual(simulations[0]['data_path'], '/data/' + str(self.pe.uid) + '/' + str(s.uid))
            self.assertEqual(simulations[0]['extra_details'], {'command': 'python ./Assets/model1.py config.json'})

            # Also test get_one with simulation id filter
            simulation = SimulationsClient.get_one(str(s.uid))
            self.assertEqual(simulations[0], simulation)

            # Also test get_one with simulation id and tags  filters
            simulation1 = SimulationsClient.get_one(str(s.uid), tags=s.tags)
            self.assertEqual(simulations[0], simulation1)

        # Test 2: get_all simulations with simulation id and experiment id as filters
        for s in self.pe.simulations:
            simulations = SimulationsClient.get_all(str(s.uid), experiment_id=str(self.pe.uid))
            self.assertEqual(simulations[0]['simulation_uid'], str(s.uid))
            self.assertEqual(simulations[0]['experiment_id'], str(self.pe.uid))
            self.assertEqual(simulations[0]['tags'], s.tags)
            self.assertEqual(simulations[0]['data_path'], '/data/' + str(self.pe.uid) + '/' + str(s.uid))
            self.assertEqual(simulations[0]['extra_details'], {'command': 'python ./Assets/model1.py config.json'})

        # Test 3: get_all simulations with experiment id as only filter
        simulations = SimulationsClient.get_all(experiment_id=str(self.pe.uid))
        for sim in simulations:
            self.assertTrue(any(sim['simulation_uid'] in simulation['simulation_uid'] for simulation in simulations))
            self.assertEqual(sim['experiment_id'], str(self.pe.uid))

    @unittest.skip("Skip")
    def test_local_runner_cli(self):
        current_dir_path = os.path.dirname(os.path.realpath(__file__))
        idmtools_local_runner_dir_path = os.path.join(current_dir_path, '..', '..', 'idmtools_local_runner')
        os.chdir(idmtools_local_runner_dir_path)

        # Test 1: get status for all simulations with experiment id
        # run cli: 'python -m idmtools_local.cli.run simulation status --experiment-id {exp_id}'
        command = ['python', '-m', 'idmtools_local.cli.run', 'simulation', 'status', '--experiment-id',
                   str(self.pe.uid)]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        print(output)

        sims_from_experiment_CLI = self.parse_simulations_from_experiment_filter_cli(output)

        # Test 2: get status for 1 simulation with simulation id and experiment id
        sims_from_simulation_CLI = []
        for s in self.pe.simulations:
            # for each simulation, run cli:
            # python -m idmtools_local.cli.run simulation status --id {s.uid}'
            command = ['python', '-m', 'idmtools_local.cli.run', 'simulation', 'status', '--id', str(s.uid)]
            output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
            print(output)
            sim = self.parse_simulations_from_experiment_filter_cli(output)[0]
            sims_from_simulation_CLI.append(sim)

        # validate test 1 and test 2 will return same result
        sims_from_simulation_CLI_sorted = sorted(sims_from_simulation_CLI,
                                                 key=itemgetter('simulation_uid', 'experiment_id'))
        sims_from_experiment_CLI_sorted = sorted(sims_from_experiment_CLI,
                                                 key=itemgetter('simulation_uid', 'experiment_id'))
        self.assertEqual(sims_from_simulation_CLI_sorted, sims_from_experiment_CLI_sorted)

        # Test 3: get status for experiment with experiment  id and tag pair
        # run experiment cli:
        # python -m idmtools_local.cli.run experiment status --id {exp_id} --tag 'idmtools' 'idmtools-automation'
        command = ['python', '-m', 'idmtools_local.cli.run', 'experiment', 'status', '--id', str(self.pe.uid), '--tags',
                   'idmtools', 'idmtools-automation']
        output_experiment = subprocess.check_output(command, stderr=subprocess.STDOUT).decode()
        print(output_experiment)
        # make sure output contains experiment id
        self.assertIn(str(self.pe.uid), output_experiment)
        self.assertIn("http://localhost:5000/data/" + str(self.pe.uid), output_experiment)
        self.assertIn(
            "{'idmtools': 'idmtools-automation', 'string_tag': 'test', 'number_tag': 123, 'type': 'idmtools_models.python.PythonExperiment'}",
            output_experiment)

    # return list of simulation dir: [{'simulation_uid':sim_id, 'experiment_id', exp_id, 'tags': tags}]
    # TODO: add status to each sim once status bug gets fixed
    def parse_simulations_from_experiment_filter_cli(self, output):
        print(output)
        count = 0
        simulation_list = []
        temp = output.split(
            "|------------------+-----------------+----------+----------------------------------------------+----------+------------------------------------------------------|")
        temp = temp[1].split('+')[0]
        lines = temp.split('\r\n')
        for line in lines:
            if count != 0 and count != len(lines) - 1:
                items = line.split("|")
                tags = items[5].strip()
                sim_uid = items[1].strip()
                exp_id = items[2].strip()
                status = self.escape_ansi(items[3])
                status = status.strip()  # wait for status bug fix to add to list
                simulation_list.append({'simulation_uid': sim_uid, 'experiment_id':
                    exp_id, 'tags': tags})
            count = count + 1
        return simulation_list

    def escape_ansi(self, line):
        ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', str(line))
