from json import JSONEncoder


class DefaultEncoder(JSONEncoder):
    """
    A default JSON encoder to naively make Python objects serializable by using their __dict__
    """
    def default(self, o):
        return o.__dict__

