import os
from os import DirEntry
from typing import Iterable


def scan_directory(basedir: str, recursive: bool = True) -> Iterable[DirEntry]:
    """
    Iterator to scan a directory recursively or not.
    Args:
        basedir: The root directory to start from.
        recursive: Whether we want to recursively scan the sub folders or stay in the root.

    Returns: An iterator yielding all the files found.

    """
    for entry in os.scandir(basedir):
        if entry.is_file():
            yield entry
        elif recursive:
            yield from scan_directory(entry.path)
