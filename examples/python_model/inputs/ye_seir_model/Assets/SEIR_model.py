import sys
import os
import random
import pandas as pd
from pathlib import Path

assets_dir = os.path.abspath(os.path.dirname(__file__))
current_directory = os.getcwd()
p_version = sys.version_info
if p_version.major == 3:
    if p_version.minor == 7:
        sys.path.append(str(Path(os.path.join(assets_dir, './MyExternalLibrary/Python37')).resolve().absolute()))
else:
    print("Sorry, this model only supports Python 3.7")
    sys.exit(1)
import dtk_nodedemog as nd
import dtk_generic_intrahost as gi
from config_sim import configure_simulation


class Constant():
    SIMULATION_TIMESTEP = "SIMULATION_TIMESTEP"
    STATISTICAL_POPULATION = "STATISTICAL_POPULATION"
    CONTAGION = "CONTAGION"
    NUM_INFECTED = "NUM_INFECTED"
    NUM_NEW_INFECTIONS = "NUM_NEW_INFECTIONS"
    hum_id = "individual_id"
    is_infected = "is_infected"
    infections = "infections"
    infectiousness = "infectiousness"
    immunity = "immunity"


class Person():
    def __init__(self, mcw, age, gender, id):
        self.mcw = mcw
        self.age = age
        self.sex = gender
        self.id = id


# Write a SEIR class using dtk_nodedemog and dtk_generic_intrahost
class SEIR():
    def __init__(self, config_template="nd_template.json", simulation_duration=10, initial_population=1000,
                 outbreak_timestep=0, outbreak_demographic_coverage=0.01, outbreak_ignore_immunity=True,
                 other_config_params: dict = None):
        """
        Define a simple SEIR model with the following parameters.
        Although this example disables fertility and mortality(natual or disease related), it's possible to
        enable vital dynamics in this model. It supports all fertility and mortality features in DTK with user
        defined birth callback and mortality callback methods.
        :param config_template: template file for configuration
        :param simulation_duration: number of time step for one simulation
        :param initial_population: number of initial population
        :param outbreak_timestep: the day to start distributing the outbreak
        :param outbreak_demographic_coverage: the fraction of individuals that will receive the outbreak
        :param outbreak_ignore_immunity: individuals will be force-infected regardless of actual immunity level when set to true
        :param other_config_params: other parameter/value pairs in config.json
        """
        self.human_pop = {}  # dictionary of individual objects at run time
        self.well_mixed_contagion_pool = []
        self.statistical_population = []
        self.num_infected = []
        self.num_new_infections = []
        self.individual_df = None
        self.node_df = None
        self.timestep = 0
        self.config_template = config_template
        self.simulation_duration = simulation_duration
        self.initial_population = initial_population
        self.outbreak_timestep = outbreak_timestep
        self.outbreak_demographic_coverage = outbreak_demographic_coverage
        self.outbreak_ignore_immunity = outbreak_ignore_immunity
        self.other_config_params = other_config_params

    def create_person_callback(self, mcw, age, gender):
        new_id = gi.create((gender, age, mcw))
        person = Person(mcw, age, gender, new_id)
        if new_id in self.human_pop:
            raise Exception(" individual {0} is already created.".format(new_id))
        else:
            self.human_pop[new_id] = person

    def expose_callback(self, action, prob, individual_id):
        random_draw = random.random()
        if self.timestep == self.outbreak_timestep:
            print(f"expose {individual_id} with outbreak.")
            if random_draw < self.outbreak_demographic_coverage:
                if self.outbreak_ignore_immunity:
                    print(f"Let's infect {individual_id} with outbreak ignore immunity.")
                    return 1
                else:
                    return self.infect_base_on_immunity(individual_id)
            else:
                print(f"Let's NOT infect {individual_id} with outbreak.")
                return 0
        else:
            print(f"expose {individual_id} with transmission.")
            if random_draw < self.well_mixed_contagion_pool[-1]:
                return self.infect_base_on_immunity(individual_id)
            else:
                print(f"Let's NOT infect {individual_id} based on random draw.")
                return 0

    def deposit_callback(self, contagion, individual):
        self.well_mixed_contagion_pool[-1] += contagion
        print(f"Depositing {contagion} contagion creates total of {self.well_mixed_contagion_pool[-1]}.")
        return

    def infect_base_on_immunity(self, individual_id):
        random_draw = random.random()
        if random_draw < gi.get_immunity(individual_id):
            print(f"Let's infect {individual_id} base on immunity.")
            return 1
        else:
            print(f"Let's NOT infect {individual_id} base on immunity.")
            return 0

    def run(self):
        """
        This is the method to run the SEIR model and generate output files.
        """
        print("\tWe cleared out human_pop. Should get populated via populate_from_files and callback...")
        gi.reset()
        nd.reset()
        self.human_pop = {}

        configure_simulation(initial_population=self.initial_population,
                             nd_template_filename=os.path.join(current_directory, self.config_template),
                             demo_template_filename=os.path.join(assets_dir, "templates/demographics_template.json"),
                             other_config_params=self.other_config_params)

        # set callbacks
        nd.set_callback(self.create_person_callback)
        nd.populate_from_files()
        gi.my_set_callback(self.expose_callback)
        gi.set_deposit_callback(self.deposit_callback)

        data = {Constant.SIMULATION_TIMESTEP: [],
                Constant.hum_id: [],
                Constant.is_infected: [],
                Constant.infectiousness: [],
                Constant.immunity: []
                }
        infected = dict()
        for t in range(self.simulation_duration):
            self.timestep = t
            # logging.info("Updating individuals at timestep {0}.".format(t))
            self.statistical_population.append(len(self.human_pop))
            self.well_mixed_contagion_pool.append(0)  # 100% decay at the end of every time step

            # this is for shedding only
            print("Updating individuals (shedding) at timestep {0}.".format(t))
            for hum_id in self.human_pop:
                nd.update_node_stats(
                    (1.0, 0.0, gi.is_possible_mother(hum_id), 0))  # mcw, infectiousness, is_poss_mom, is_infected
                gi.update1(hum_id)  # this should do shedding

            # Normalize contagion
            if self.well_mixed_contagion_pool[-1] > 0:
                self.well_mixed_contagion_pool[-1] /= len(self.human_pop)
            print("well_mixed_contagion_pool = {0}.".format(self.well_mixed_contagion_pool[-1]))

            print("Updating individuals (exposing) at timestep {0}.".format(t))
            self.num_infected.append(0)
            self.num_new_infections.append(0)
            for hum_id in list(self.human_pop.keys()):  # avoid "RuntimeError: dictionary changed size during iteration"
                gi.update2(hum_id)  # this should do exposure & vital-dynamics(turn off in this example)
                # Collect individual level data for every time step
                data[Constant.SIMULATION_TIMESTEP].append(t)
                data[Constant.hum_id].append(hum_id)
                data[Constant.is_infected].append(gi.is_infected(hum_id))
                data[Constant.infectiousness].append(round(gi.get_infectiousness(hum_id), 6))
                data[Constant.immunity].append(gi.get_immunity(hum_id))
                if gi.is_infected(hum_id):
                    self.num_infected[-1] += 1
                    if hum_id not in infected or not infected[hum_id]:
                        self.num_new_infections[-1] += 1
                    infected[hum_id] = 1
                else:
                    infected[hum_id] = 0

            print(f"num_infected = {self.num_infected[-1]}.")
            # End of one timestep

        # save individual level and node level data
        self.individual_df = pd.DataFrame.from_dict(data)
        self.individual_df.index.name = "index"

        self.node_df = pd.DataFrame.from_dict({Constant.STATISTICAL_POPULATION: self.statistical_population,
                                               Constant.CONTAGION: self.well_mixed_contagion_pool,
                                               Constant.NUM_INFECTED: self.num_infected,
                                               Constant.NUM_NEW_INFECTIONS: self.num_new_infections})
        self.node_df.index.name = "TimeStep"

        if self.individual_df.empty or self.node_df.empty:
            print("BAD: Simulation data is empty.")

        print("writing result:")
        self.write()
        print("Simulation exits.")
        pass

    def write(self, output_path="output", node_filename="node.csv", individual_filename="individual.csv"):
        output_path = os.path.join(current_directory, output_path)
        if not os.path.exists(output_path):
            print(f"making output folder {output_path}")
            os.makedirs(output_path)

        with open(os.path.join(output_path, individual_filename), 'w') as individual_file:
            print(f"writing to {os.path.join(output_path, individual_filename)} now")
            self.individual_df.to_csv(individual_file, line_terminator="\n")

        with open(os.path.join(output_path, node_filename), 'w') as node_file:
            print(f"writing to {os.path.join(output_path, node_filename)} now")
            self.node_df.to_csv(node_file, line_terminator="\n")


if __name__ == "__main__":
    # execute only if run as a script
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--config', default="nd_template.json",
                        help="config file name(default to nd_template.json)")
    parser.add_argument('-d', '--duration', default=10, help="simulation duration(number of time steps)(default to 10)")
    parser.add_argument('-p', '--population', default=1000, help="number of initial population(default to 100)")
    parser.add_argument('-o', '--outbreak', default=0, help="outbreak time step(default to 0)")
    parser.add_argument('-c', '--outbreak_coverage', default=0.01,
                        help="demographic coverage for outbreak(default to 0.1)")
    parser.add_argument('-i', '--outbreak_ignore_immunity',
                        help="if outbreak ignore the immunity status(default to True)", action='store_true')
    args = parser.parse_args()

    model = SEIR(config_template=args.config,
                 simulation_duration=int(args.duration),
                 initial_population=int(args.population),
                 outbreak_timestep=int(args.outbreak),
                 outbreak_demographic_coverage=float(args.outbreak_coverage),
                 outbreak_ignore_immunity=args.outbreak_ignore_immunity)
    model.run()
    # The local platform needs to know the resulting status of a work item. We provide it through a return code
    sys.exit(0)
