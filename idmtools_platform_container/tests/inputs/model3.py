import os

from MyLib.functions import add
current_dir = os.path.abspath(os.getcwd())
if __name__ == "__main__":
    import json

    with open("config.json", 'r') as fp:
        config = json.load(fp)
        parameters = config["parameters"]

    result = add(parameters["a"], parameters["b"])
    print(result)
    print(config["parameters"])

    output_dir = os.path.join(current_dir, "output")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    with open(os.path.join(output_dir, "result.txt"), "w") as fp:
        fp.write("result:")
        fp.write(str(result))
