import os
import sys

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site_packages')  # Need to site_packages level!!!

sys.path.insert(0, LIBRARY_PATH)  # Very Important!
import pytest

def inc(x):
    return x + 2

def test_answer():
    assert inc(3) == 5


if __name__ == "__main__":
    test_answer()
