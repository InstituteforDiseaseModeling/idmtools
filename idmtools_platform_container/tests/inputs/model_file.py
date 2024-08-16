import os
import sys
import ast
import inspect

dir_path = os.path.dirname(__file__)  # working
sys.path.append(os.path.join(dir_path, "site-packages"))  # Need to site-packages level!!!

import astor


def dump_tree():
    src = inspect.getsource(ast)
    expr_ast = ast.parse(src)
    print(astor.dump_tree(expr_ast))  # one line

if __name__ == "__main__":
    dump_tree()