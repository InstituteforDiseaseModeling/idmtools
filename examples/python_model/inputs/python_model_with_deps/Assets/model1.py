import json
import os
import sys

if __name__ == "__main__":
    current_directory = os.path.abspath(os.getcwd())
    with open("config.json", 'r') as fp:
        config = json.load(fp)
        run_number = config["Run_Number"]
        a = config["a"]
        b = config["b"]

    os.makedirs(os.path.join(current_directory, "output"))
    with open(os.path.join(current_directory, "output", "output.json"), 'w') as fp:
        json.dump({"Run_Number": run_number}, fp)
        json.dump({"a": a}, fp)
        json.dump({"b": b}, fp)

    sys.exit(0)
