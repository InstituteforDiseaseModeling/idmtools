import os


def del_file(filename, dir=None):
        if dir:
            filepath = os.path.join(dir, filename)
        else:
            filepath = os.path.join(os.path.curdir, filename)

        if os.path.exists(filepath):
            print(filepath)
            os.remove(filepath)
