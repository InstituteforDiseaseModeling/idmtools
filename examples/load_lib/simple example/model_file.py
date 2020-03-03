import os
import sys
import ast
import inspect

CURRENT_DIRECTORY = os.path.dirname(__file__)
LIB_PATH = os.path.join(CURRENT_DIRECTORY, 'site_packages')  # Need to site_packages level!!!
# LIB_PATH = LIB_PATH.replace('\\', '/')        # optional

sys.path.insert(0, LIB_PATH)  # Very Important!
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
