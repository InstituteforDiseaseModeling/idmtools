import json
import os
import sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "Libraries"))


output_dir = os.path.join(dir_path, "..", "output")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

config = json.load(open(os.path.join(dir_path, "..", "config.json"), "r"))
print(config)

with open(os.path.join(output_dir, "result.json"), "w") as fp:
    json.dump(config, fp)
