import os
import sys
import ast
import inspect

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIBRARY_PATH = os.path.join(CURRENT_DIRECTORY, 'site_packages')  # Need to site_packages level!!!

# we will search 'astor' package from Assets/site_package first then other system path
# that is why we need inset to sys.path index '0', instead of appending to the end in sys path
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
