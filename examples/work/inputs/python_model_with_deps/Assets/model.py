import sys
from MyExternalLibrary.functions import add

if __name__ == "__main__":
    import json

    with open("config.json", 'r') as fp:
        parameters = json.load(fp)

    print(add(parameters["a"], parameters["b"]))
    print(parameters)

    # The local platform needs to know the resulting status of a work item. We provide it through a return code
    # 0 means succeeded. Any other value is an error. It is optional if you want to provide specific return codes
    # for specific errors
    sys.exit(0)