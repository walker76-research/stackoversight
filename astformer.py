import ast
from pprint import pprint
from enum import Enum

DEBUG = True

class ASTFormerStatus(Enum):
    SUCCESS = 1
    FAILURE = 0

class ASTFormer:
    # Create an object of ASTFormer with the Python source code
    # to create an abstract syntax tree of the code. form_ast()
    # iterates the tree.
    # Sets status to SUCCESS if valid Python code (determined by if AST can be formed).
    def __init__(self, source):
        self.source = source
        self.stats = {"import": [], "from": []}
        self.code = source
        try:
            self.tree = ast.parse(str(source))
            self.status = ASTFormerStatus.SUCCESS
        except SyntaxError:
            self.tree = None
            self.status = ASTFormerStatus.FAILURE
            if DEBUG:
                pprint("Failed to create syntax tree. Cannot compile the code to Python.")
                pprint(SyntaxError)
        except:
            self.tree = None
            self.status = ASTFormerStatus.FAILURE
            if DEBUG: pprint("Unknown error")

    def form_ast(self):
        if self.status == ASTFormerStatus.SUCCESS:
            analyzer = ASTIterator()
            analyzer.visit(self.tree)

    def dump(self):
        if self.status == ASTFormerStatus.SUCCESS:
            return ast.dump(self.tree)
        else:
            return None

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