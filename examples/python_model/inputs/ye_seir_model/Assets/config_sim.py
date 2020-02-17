import json

class DemographicsParameters():
    Nodes = "Nodes"
    NodeAttributes = "NodeAttributes"
    InitialPopulation = "InitialPopulation"

def get_json_template(json_filename="demographics_template.json"):
    with open(json_filename) as infile:
        j_file_obj = json.load(infile)
    return j_file_obj

def set_demographics_file(demographics, demo_filename="demographics.json"):
    with open(demo_filename, 'w') as outfile:
        json.dump(demographics, outfile, indent=4, sort_keys=True)

def set_config_file(config, config_filename="nd.json"):
    with open(config_filename, 'w') as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)

def set_gi_file(config, gi_filename="gi.json"):
    with open(gi_filename, 'w') as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True)

def configure_simulation(initial_population,
                         nd_template_filename,
                         demo_template_filename,
                         other_config_params: dict = None):
    print("configure demographics.json.\n")
    demographics = get_json_template(json_filename=demo_template_filename)
    demographics[DemographicsParameters.Nodes][0][DemographicsParameters.NodeAttributes][
        DemographicsParameters.InitialPopulation] = initial_population
    set_demographics_file(demographics)

    print("configure nd.json and gi.json.\n")
    config = get_json_template(json_filename=nd_template_filename)

    if other_config_params:
        for param in other_config_params:
            config[param] = other_config_params[param]
    set_config_file(config)
    set_gi_file(config)