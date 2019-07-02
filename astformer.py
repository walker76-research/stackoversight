import ast
from pprint import pprint

class ASTFormer:
    # Create an object of ASTFormer with the Python source code
    # to create an abstract syntax tree of the code. form_ast()
    # iterates the tree.
    def __init__(self, source):
        self.source = source
        self.tree = ast.parse(str(source))
        self.stats = {"import": [], "from": []}
        self.code = source

    def form_ast(self):
        analyzer = ASTIterator()
        analyzer.visit(self.tree)

    def dump(self):
        return ast.dump(self.tree)

    def dump_tofile(self):
        out = open("dump_file.txt", "w")
        out.write((self.dump()))
        out.close()
        return "written to file " + out.name

    def report(self):
        pprint(self.stats)

class ASTIterator(ast.NodeVisitor):
    # Class for traversing the AST tree.
    def __init__(self):
        self.stats = {"import": [], "from": []}

    # (found online) finds the import packages and appends to
    # stats attribute of ASTFormer.
    def visit_Import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    # (found online) finds the from imports and appends to
    # stats attribute of ASTFormer.
    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)
