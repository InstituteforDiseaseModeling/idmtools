import os
import pandas as pd
import shutil

from idmtools.entities.simulation import Simulation


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


def load_csv_file(filename, dir=None):
    df = None
    if dir:
        filepath = os.path.join(dir, filename)
    else:
        filepath = os.path.join(os.path.curdir, filename)

    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
    return df


def verify_simulation(simulation:Simulation, expected_parameters, expected_values):
    for value_set in expected_values:
        for i, value in enumerate(list(value_set)):
            if not simulation.task.parameters[expected_parameters[i]] == expected_values:
                break
        return True
    return False