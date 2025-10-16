import ast
import astor
import os
from pathlib import Path

def main():
    # Sample Python code
    source_code = """
def add(a, b):
    return a + b
    """

    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Dump the AST tree to a string
    tree_str = astor.dump_tree(tree)

    # File path to save the AST dump
    file_path = 'ast_dump.txt'

    # Write the AST string to a file under output dir
    os.makedirs("output", exist_ok=True)
    with open(Path("output") / file_path, 'w') as file:
        file.write(tree_str)

    print(f"AST dump written to {file_path}")

if __name__ == "__main__":
    main()

