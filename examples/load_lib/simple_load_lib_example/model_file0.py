import ast
import inspect
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
