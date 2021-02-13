import csv
import json
import os
import sys
from MyExternalLibrary.functions import add


if __name__ == "__main__":
    current_directory = os.path.abspath(os.getcwd())

    # read config.json to dict
    with open("config.json", 'r') as fp:
        config_dict = json.load(fp)
        parameters = config_dict['parameters']
        parameters["d"] = add(parameters["a"], parameters["b"])

    # write to csv file
    os.makedirs(os.path.join(current_directory, "output"))
    with open(os.path.join(current_directory, "output", "a.csv"), 'w') as fpa:
        fieldnames = ['first_name', 'last_name']
        writer = csv.DictWriter(fpa, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
        writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
        writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})

    # write to csv file
    with open(os.path.join(current_directory, "output", "b.csv"), 'w') as fpb:
        fieldnames = ['age', 'city']
        writer = csv.DictWriter(fpb, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({'age': '5', 'city': 'seattle'})
        writer.writerow({'age': '10', 'city': 'kirkland'})
        writer.writerow({'age': '10', 'city': 'bellevue'})

    # write to csv file
    with open(os.path.join(current_directory, "output", "c.csv"), 'w') as f:
        fieldnames = ['parameter', 'run_number']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key in sorted(parameters.keys()):
            f.write("%s,%s\n" % (key, parameters[key]))

    sys.exit(0)
