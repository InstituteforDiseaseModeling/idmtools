import json
import time

if __name__ == "__main__":
    with open("config.json", 'r') as fp:
        param = json.load(fp)["Run_Number"]
        if param == 0 or param == 2 or param == 4:
            raise Exception("Exception!")
    time.sleep(3)
    print("Done")
