import json
import time

if __name__ == "__main__":
    with open("config.json", 'r') as fp:
        param = json.load(fp)["parameters"]["P"]
        if param == 2:
            raise Exception("Exception!")
    time.sleep(3)
    print("Done")
