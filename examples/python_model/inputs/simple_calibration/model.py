import json

if __name__ == "__main__":
    with open("config.json", 'r') as fp:
        config = json.load(fp)
        a = config["parameters"]["a"]
        b = config["parameters"]["b"]

    with open("output.json", 'w') as fp:
        output = {"result": a + b}
        json.dump(output, fp)
