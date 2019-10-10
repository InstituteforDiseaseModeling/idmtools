import json
import os
import sys

# dir_path is current file dir which is under "Assets" dir in COMPS
current_dir = os.path.abspath(os.getcwd())
assets_path = os.path.join(current_dir, "Assets")
sys.path.append(os.path.join(assets_path, "MyExternalLibrary"))

# create 'output' dir in COMPS under current working dir which is one dir above "Assets" dir
output_dir = os.path.join(current_dir, "output")
config_path = os.path.join(current_dir, "config.json")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

config = json.load(open(config_path, "r"))
print(config)

# write each configs to result.json in comps's simulation output
with open(os.path.join(output_dir, "result.json"), "w") as fp:
    json.dump(config, fp)
