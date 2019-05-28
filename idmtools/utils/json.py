from json import JSONEncoder


class DefaultEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

