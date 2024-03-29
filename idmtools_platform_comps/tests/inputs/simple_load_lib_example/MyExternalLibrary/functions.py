import os
import sys

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, '..', 'site-packages')  # Need to site-packages level!!!

sys.path.insert(0, LIBRARY_PATH)

import numpy as np  # noqa


def add(x, y):
    """
    Add x to y

    Args:
        x: x to add
        y: y to add

    Returns:

    """
    return np.add(x, y)
