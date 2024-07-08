"""
Here we implement the ContainerPlatform utils.

Copyright 2021, Bill & Melinda Gates Foundation. All rights reserved.
"""
import os
import uuid
import math
from pathlib import Path
from typing import Union
from datetime import datetime
import platform as platform
from logging import getLogger

logger = getLogger(__name__)
user_logger = getLogger('user')


#############################
# Utility Functions
#############################

def normalize_path(path: Union[str, Path]):
    """
    Normalize the binding path to handle case insensitivity and path separators for Windows.
    Args:
        path (str): The path to normalize.
    Returns:
        str: The normalized path.
    """
    path = str(path)
    if platform.system() == 'Windows':
        path = path.lower()
    path = os.path.normpath(path).replace('\\', '/')
    return path.rstrip('/')


def map_container_path(source_binding, destination_binding, source_path) -> str:
    """
    Map a source path to its corresponding destination path within the container.
    Args:
        source_binding (str): The source directory in the binding (e.g., /abc/my_path).
        destination_binding (str): The destination directory in the container (e.g., /home/my_path).
        source_path (str): The source file or folder path to map (e.g., /abc/my_path/file_or_folder_path).
    Returns:
        str: The corresponding destination path within the container (e.g., /home/my_path/file_or_folder_path).

    Raises:
        ValueError: If the source path does not start with the source binding path.
    """
    source_path = str(source_path)
    # Normalize binding paths
    normalized_source_binding = normalize_path(source_binding)
    normalized_source_path = normalize_path(source_path)

    # Ensure the source path starts with the source binding
    if not normalized_source_path.startswith(normalized_source_binding):
        raise ValueError("Source path does not start with the source binding path")

    # Compute the relative path from the source binding to the source path
    relative_path = os.path.relpath(source_path, source_binding)

    # Combine the destination binding with the relative path
    destination_path = os.path.join(destination_binding, relative_path)

    # Normalize the destination path to ensure proper path separators and convert to Unix-style path
    destination_path = normalize_path(destination_path)

    return destination_path


# Function to convert ISO 8601 format string to a datetime object
def parse_iso8601(date_str):
    """
    Convert an ISO 8601 format string to a datetime object.
    Args:
        date_str: time string in ISO 8601 format
    Returns:
        datetime object
    """
    # Truncate the fractional seconds to a maximum of 6 digits
    if '.' in date_str:
        date_str = date_str[:date_str.index('.') + 7] + 'Z'
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


def is_valid_uuid(uuid_to_test, version=4) -> bool:
    """
    Check if the provided string is a valid UUID.
    Args:
        uuid_to_test: UUID string to test
        version: test against a specific UUID version
    Returns:
        True/False
    """
    try:
        # check for validity of Uuid
        _ = uuid.UUID(uuid_to_test, version=version)
        return True
    except ValueError:
        return False


def convert_byte_size(size_bytes: int) -> str:
    """
    Convert byte size to human-readable.
    Args:
        size_bytes: byte site in integer
    Returns:
        str: human-readable size
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])
