import json
from json import JSONEncoder


class DefaultEncoder(JSONEncoder):
    """
    A default JSON encoder to naively make Python objects serializable by using their __dict__.
    """

    def default(self, o):
        return o.__dict__


def load_json_file(path):
    if not path:
        return
    try:
        with open(path, 'r') as fp:
            return json.load(fp)
    except IOError as e:
        print(f"The file at {path} could not be loaded or parsed to JSON.\n{e}")
