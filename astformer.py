import ast
from pprint import pprint
from enum import Enum
from sanitizecode import SanitizeCode


class ASTFStatus(Enum):
    SUCCESS = 1
    PROCESSING = 0
    FAILURE = -1


class ASTFormer:
    # Create an object of ASTFormer with the Python source code
    # to create an abstract syntax tree of the code. form_ast()
    # iterates the tree.
    # Sets status to SUCCESS if valid Python code (determined by if AST can be formed).
    def __init__(self, source):
        self.source = source
        self.stats = {"import": [], "from": []}
        self.code = source
        self.status = ASTFStatus.PROCESSING
        self.faulty_lines = []
        try:
            self.tree = ast.parse(str(source))
            self.status = ASTFStatus.SUCCESS
        except IndentationError as e:                   # TODO: handle more types of exceptions and sanitize as needed
            san_code = SanitizeCode(self.source)        # sanitzation handler
            san_code.clean_false_indents()              # attempts to clean up indentation errors
            try:
                self.tree = ast.parse(san_code.code)    # attempt re-parse
                self.status = ASTFStatus.SUCCESS
            except Exception as e:                              # there is an exception remaining that is not indentation.
                self.status = ASTFStatus.FAILURE                # could abstract this out into a loop and run until no
                if self.debug_mode(): self.debug_exception(e)   # exceptions are given under a given loop threshold.
        except SyntaxError as e:                        # The exception is not indentation related initially.
            self.tree = None
            self.status = ASTFStatus.FAILURE
            if self.debug_mode(): self.debug_exception(e)

    def debug_exception(self, e):
        pprint("Failed to create syntax tree. Cannot compile the code to Python.")
        pprint(self.code)
        print(getattr(e, 'message', repr(e)))
        self.faulty_line = e.lineno

    def form_ast(self):
        if self.status == ASTFStatus.SUCCESS:
            analyzer = ASTIterator()
            analyzer.visit(self.tree)

    def dump(self):
        if self.status == ASTFStatus.SUCCESS:
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

    @staticmethod
    def debug_mode(mode=False):  # Sets debug mode on or off
        return mode


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