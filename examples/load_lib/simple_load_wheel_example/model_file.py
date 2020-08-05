import ast
import inspect
import os
import sys

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site-packages')  # Need to site-packages level!!!

"""
sys.path.insert(0, LIBRARY_PATH) will search packages from experiment's 'Assets/site-packages' first,
then default HPC python site-packages.
"astor" package does not exist in comps, so we use custom_lib to upload to experiment's Assets/site-packages directory
Please go to examples/load_lib/example-load-lib.py to see how we upload 'astor' package to comps
"""
sys.path.insert(0, LIBRARY_PATH)  # Very Important!
print(sys.path)

import astor


def dump_tree():
    print('astor version: ', astor.__version__)
    print('astor path: ', astor.__path__)
    print(astor)

    src = inspect.getsource(ast)
    expr_ast = ast.parse(src)

    print(astor.dump_tree(expr_ast))


if __name__ == "__main__":
    dump_tree()
