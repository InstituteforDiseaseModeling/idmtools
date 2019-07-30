from os.path import dirname, realpath, join, abspath

current_directory = dirname(realpath(__file__))
INPUT_PATH = join(current_directory, "inputs")
COMMON_INPUT_PATH = abspath(join(current_directory, '..', 'idmtools', 'tests', 'inputs'))