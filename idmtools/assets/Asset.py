import os


class Asset:

    def __init__(self, absolute_path: str = None, relative_path: str = None,
                 filename: str = None, content: bytes = None):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.filename = filename or os.path.basename(self.absolute_path)
        self._content = content

    def __repr__(self):
        return f"<Asset: {os.path.join(self.relative_path, self.filename)} from {self.absolute_path}>"

    @property
    def content(self):
        if self._content: return self._content

        with open(self.absolute_path, "r") as fp:
            return fp.read()

    # region Equality and Hashing
    def __eq__(self, other):
        return self.__key() == other.__key()

    def __key(self):
        return self.absolute_path, self.relative_path, self.filename

    def __hash__(self):
        return hash(self.__key())
    # endregion
