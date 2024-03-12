"""
utilities for files.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
from os import DirEntry
from typing import Iterable, Generator, List, Dict

from idmtools.assets import Asset


def scan_directory(basedir: str, recursive: bool = True, ignore_directories: List[str] = None) -> Iterable[DirEntry]:
    """
    Scan a directory recursively or not.

    Args:
        basedir: The root directory to start from.
        recursive: True to search the sub-folders recursively; False to stay in the root directory.
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


def file_contents_to_generator(absolute_path, chunk_size=128) -> Generator[bytearray, None, None]:
    """
    Create a generator from file contents in chunks(useful for streaming binary data and piping).

    Args:
        absolute_path: absolute path to file
        chunk_size: chunk size

    Returns:
        Generator that return bytes in chunks of size chunk_size
    """
    with open(absolute_path, 'rb') as i:
        while True:
            res = i.read(chunk_size)
            if res == b'':
                break
            else:
                yield res


def file_content_generator(content, chunk_size=128) -> Generator[bytearray, None, None]:
    """
    Create a generator from file contents in chunks(useful for streaming binary data and piping).

    Args:
        content : file content
        chunk_size : chunk size

    Returns:
        Generator that return bytes in chunks of size chunk_size
    """
    if content:
        content_size = len(content)
        if content_size == 0:
            yield b''
            return
        # Generate chunks from content
        for start in range(0, content_size, chunk_size):
            end = start + chunk_size
            yield content[start:end].encode()


def write_md5_to_file(asset_dict: Dict):
    """
    Write md5 as content to file.

    Args:
        asset_dict ():

    Returns:
        None
    """
    for filename, md5 in asset_dict.items():
        asset = Asset(filename=f"{filename}.asset_id", checksum=md5, content=f"{filename}:asset_id:{md5}")
        asset.download_asset(os.path.curdir)
