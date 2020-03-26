import os
import sys

CURRENT_DIRECTORY = os.path.dirname(__file__)

sys.path.insert(0, CURRENT_DIRECTORY)

from MyExternalLibrary.functions import add

if __name__ == "__main__":
    import json

    with open("config.json", 'r') as fp:
        config = json.load(fp)
        parameters = config["parameters"]

    print(add(parameters["a"], parameters["b"]))
    print(config["parameters"])
