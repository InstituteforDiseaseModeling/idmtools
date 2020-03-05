import json
import os
import sys
import ast
import inspect
# from COMPS.Data import Experiment

# dir_path = os.path.dirname(os.path.realpath(__file__))    # working
# from idmtools.entities.experiment import Experiment
# from idmtools.entities.experiment import Experiment

dir_path = os.path.dirname(__file__)  # working
sys.path.append(os.path.join(dir_path, "lib", "site-packages"))  # Need to site-packages level!!!

# print('dir_path: \n', dir_path)
# print(os.path.join(dir_path, "Assets", "lib", "site-packages"))

import astor


def dump_tree():
    # src = inspect.getsource(SimpleVaccine)
    src = inspect.getsource(ast)
    # src = inspect.getsource(A)
    expr_ast = ast.parse(src)

    # print(ast.dump(expr_ast))  # one line
    print(astor.dump_tree(expr_ast))  # one line
    # print(codegen.dump(expr_ast))                 # one line ast dump
    # print(astunparse.dump(expr_ast))                # JSON format


if __name__ == "__main__":
    dump_tree()