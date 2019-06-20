import os
from typing import Union


class Asset:
    """
    Class representing an asset.
    An asset can either be related to a physical asset present on the computer or directly specified by a filename
    and content.
    """

    def __init__(self, absolute_path: 'str' = None, relative_path: 'str' = None,
                 filename: 'str' = None, content: 'Union[bytes,str]' = None):
        """
        Constructor.
        Args:
            absolute_path: The absolute path of the asset. Optional if filename/content specified
            relative_path:  The relative path (compared to the simulation root folder)
            filename: Name of the file. Optional if a absolute_path is given
            content: The content of the file. Optional if absolute path is given
        """

        if not absolute_path and not filename and not content:
            raise ValueError("Impossible to create the asset without either absolute path or filename and content!")

        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.filename = filename or os.path.basename(self.absolute_path)
        self._content = content

    def __repr__(self):
        return f"<Asset: {os.path.join(self.relative_path, self.filename)} from {self.absolute_path}>"

    @property
    def relative_path(self):
        return self._relative_path or ""

    @relative_path.setter
    def relative_path(self, relative_path):
        self._relative_path = relative_path.strip(" \\/") if relative_path else None

    @property
    def content(self) -> bytes:
        """
        Returns: content of the file. Either from the content attribute or by opening the absolute path.
        """
        if self._content:
            return self._content if isinstance(self._content, bytes) else str.encode(self._content)

        with open(self.absolute_path, "rb") as fp:
            return fp.read()

    # region Equality and Hashing
    def __eq__(self, other):
        return self.__key() == other.__key()

    def __key(self):
        return self.absolute_path, self.relative_path, self.filename, self._content

    def __hash__(self):
        return hash(self.__key())
    # endregion
