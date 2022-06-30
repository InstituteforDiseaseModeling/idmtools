from MyLib.functions import add

if __name__ == "__main__":
    import json

    with open("config.json", 'r') as fp:
        config = json.load(fp)
        parameters = config["parameters"]

    print(add(parameters["a"], parameters["b"]))
    print(config["parameters"])
