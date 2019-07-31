import json
import os
import sys

# dir_path is current file dir which is under "Assets" dir in COMPS
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, "MyExternalLibrary"))

# create 'output' dir in COMPS under current working dir which is one dir above "Assets" dir
output_dir = os.path.join(dir_path, "..", "output")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

config = json.load(open(os.path.join(dir_path, "..", "config.json"), "r"))
print(config)

# write each configs to result.json in comps's simulation output
with open(os.path.join(output_dir, "result.json"), "w") as fp:
    json.dump(config, fp)
