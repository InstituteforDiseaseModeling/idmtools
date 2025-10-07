import json
import os
import sys

if __name__ == "__main__":
    current_directory = os.path.abspath(os.getcwd())
    with open("config.json", 'r') as fp:
        config = json.load(fp)
        run_number = config["a"]

    os.makedirs(os.path.join(current_directory, "output"), exist_ok = True)
    with open(os.path.join(current_directory, "output", "output.json"), 'w') as fp:
        json.dump({"a": run_number}, fp)

    print(f"Simulation running with Run_Number = {run_number}")

    sys.exit(0)
