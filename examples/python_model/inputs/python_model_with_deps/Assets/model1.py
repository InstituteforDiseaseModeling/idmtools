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


    # The local platform needs to know the resulting status of a work item. We provide it through a return code
    # print(f"Simulation running with Run_Number = {run_number}")
    # 0 means succeeded. Any other value is an error. It is optional if you want to provide specific return codes
    # for specific errors
    sys.exit(0)
