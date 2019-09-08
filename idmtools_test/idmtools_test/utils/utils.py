import os
import pandas as pd
import shutil

def del_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def del_file(filename, dir=None):
    if dir:
        filepath = os.path.join(dir, filename)
    else:
        filepath = os.path.join(os.path.curdir, filename)

    if os.path.exists(filepath):
        print(filepath)
        os.remove(filepath)