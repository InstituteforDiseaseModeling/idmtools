import os
from os import DirEntry
from typing import Iterable, Generator


def scan_directory(basedir: str, recursive: bool = True) -> Iterable[DirEntry]:
    """
    Scan a directory recursively or not.

    Args:
        basedir: The root directory to start from.
        recursive: True to search the subfolders recursively; False to stay in the root directory.

    Returns:
        An iterator yielding all the files found.
    """
    for entry in os.scandir(basedir):
        if entry.is_file():
            yield entry
        elif recursive:
            yield from scan_directory(entry.path)


def file_contents_to_generator(filename, chunk_size=128) -> Generator[bytearray, None, None]:
    """
    Create a generator from file contents in chunks(useful for streaming binary data and piping)
    Args:
        filename:
        chunk_size:

    Returns:

    """
    with open(filename, 'rb') as i:
        while True:
            res = i.read(chunk_size)
            if res == '':
                break
            else:
                yield res
