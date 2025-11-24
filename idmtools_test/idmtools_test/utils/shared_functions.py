from operator import itemgetter
from COMPS.Data import Experiment as COMPSExperiment, QueryCriteria


def validate_output(self, exp_id, expected_sim_count):
    sim_count = 0
    for simulation in COMPSExperiment.get(exp_id).get_simulations():
        sim_count = sim_count + 1
        result_file_string = simulation.retrieve_output_files(paths=['output/result.json'])
        print(result_file_string)
        config_string = simulation.retrieve_output_files(paths=['config.json'])
        print(config_string)
        self.assertEqual(result_file_string, config_string)

    self.assertEqual(sim_count, expected_sim_count)


def validate_sim_tags(self, exp_id, expected_tags):
    tags = []
    for simulation in COMPSExperiment.get(exp_id).get_simulations():
        tags.append(simulation.get(simulation.id, QueryCriteria().select_children('tags')).tags)

    sorted_tags = sorted(tags, key=itemgetter('a'))
    sorted_expected_tags = sorted(expected_tags, key=itemgetter('a'))
    self.assertEqual(sorted_tags, sorted_expected_tags)
