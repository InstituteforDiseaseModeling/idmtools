from MyExternalLibrary.functions import add

if __name__ == "__main__":
    import json

    with open("config.json", 'r') as fp:
        parameters = json.load(fp)

    print(add(parameters["a"], parameters["b"]))
    print(parameters)
