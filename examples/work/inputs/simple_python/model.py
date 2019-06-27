import json

if __name__ == "__main__":

    with open("config.json", 'r') as fp:
        config = json.load(fp)
        run_number = config["Run_Number"]

    print(f"Simulation running with Run_Number = {run_number}")
