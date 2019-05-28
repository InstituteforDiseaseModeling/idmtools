import os
from os import DirEntry
from typing import Iterable


def scan_directory(baseDir: str, recursive: bool = True) -> Iterable[DirEntry]:
    for entry in os.scandir(baseDir):
        if entry.is_file():
            yield entry
        elif recursive:
            yield from scan_directory(entry.path)
