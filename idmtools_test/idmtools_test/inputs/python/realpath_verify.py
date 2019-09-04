import os

# This file is used to verify consistent file paths for realpath across platforms

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
