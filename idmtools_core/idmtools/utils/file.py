import os
from os import DirEntry
from typing import Iterable, Generator, List


def scan_directory(basedir: str, recursive: bool = True, ignore_directories: List[str] = None) -> Iterable[DirEntry]:
    """
    Scan a directory recursively or not.

    Args:
        basedir: The root directory to start from.
        recursive: True to search the subfolders recursively; False to stay in the root directory.
        ignore_directories: Ignore directories

    Returns:
        An iterator yielding all the files found.
    """
    for entry in os.scandir(basedir):
        if entry.is_file():
            yield entry
        elif recursive:
            if ignore_directories is None or entry.name not in ignore_directories:
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
            if res == b'':
                break
            else:
                yield res
