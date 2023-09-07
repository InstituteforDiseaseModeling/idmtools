import os
import sys

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site-packages')  # Need to site-packages level!!!

"""
sys.path.insert(0, LIBRARY_PATH) will search packages from experiment's 'Assets/site-packages' first,
then default HPC python site-packages.
"astor" package does not exist in comps, so we use custom_lib to upload to experiment's Assets/site-packages directory
Please go to examples/load_lib/example-load-lib.py to see how we upload 'astor' package to comps
"""
sys.path.insert(0, LIBRARY_PATH)
sys.path.append(os.path.join(CURRENT_DIRECTORY))
print(sys.path)
from MyExternalLibrary.functions import add

if __name__ == "__main__":
    import json

    with open("config.json", 'r') as fp:
        config = json.load(fp)
        parameters = config["parameters"]

    print(add(parameters["a"], parameters["b"]))
    print(config["parameters"])
