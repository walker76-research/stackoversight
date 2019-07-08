import ast
import copy
from pprint import pprint
from enum import Enum
from sanitizecode import SanitizeCode


# TODO: Go line by line and remove lines of code that are comments or plaintext
# TODO: Sanitizer and Filter files
class ASTFStatus(Enum):
    SUCCESS = 1
    PROCESSING = 0
    FAILURE = -1


class ASTFormer:
    # Create an object of ASTFormer with the Python source code
    # to create an abstract syntax tree of the code. form_ast()
    # iterates the tree.
    # Sets status to SUCCESS if valid Python code (determined by if AST can be formed).
    MAX_ITERATIONS = 25

    def __init__(self, source):
        self.stats = {"import": [], "from": []}
        self.code = source
        self.status = ASTFStatus.PROCESSING
        self.faulty_line = -1
        self.iterations = 0
        self.tree = None
        self.code = self.remove_plaintext(self.code)
        code_sanitizer = SanitizeCode(self.code)
        code_sanitizer.strip_comments()
        self.code = code_sanitizer.code
        while self.status is not ASTFStatus.SUCCESS and self.iterations < ASTFormer.MAX_ITERATIONS:
            self.sanitize()
            self.iterations = self.iterations + 1
        if self.debug_mode():
            if self.status == ASTFStatus.SUCCESS:
                print("AST Formed Successfully, resolved " + str(self.iterations) + " errors.")
                print(self.code)
            else:
                print("Could not form AST.")

    def sanitize(self):
        try:
            self.tree = ast.parse(str(self.code))
            self.status = ASTFStatus.SUCCESS
        except IndentationError as e:                               # TODO: handle more types of exceptions and sanitize as needed
            if e.args[0] == "unexpected indent":
                san_code = SanitizeCode(self.code)                  # sanitzation handler
                san_code.clean_false_indents()                      # attempts to clean up indentation errors
                self.code = san_code.code
                try:
                    self.tree = ast.parse(self.code)                # attempt re-parse
                    self.status = ASTFStatus.SUCCESS
                except Exception as e:                              # there is an exception remaining that is not indentation.
                    self.status = ASTFStatus.FAILURE                # could abstract this out into a loop and run until no
                    if self.debug_mode(): self.debug_exception(e)   # exceptions are given under a given loop threshold.
            elif e.args[0] == "expected an indented block":
                san_code = SanitizeCode(self.code)
                san_code.add_indents(e.args[1][1]-1)
                self.code = san_code.code
                try:
                    self.tree = ast.parse(self.code)
                    self.status = ASTFStatus.SUCCESS
                except Exception as e:
                    self.status = ASTFStatus.FAILURE
                    if self.debug_mode(): self.debug_exception(e)
        except SyntaxError as e:                                    # The exception is not indentation related initially.
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

    def dump_to_file(self):
        out = open("dump_file.txt", "w")
        out.write((self.dump()))
        out.close()
        return "written to file " + out.name

    def report(self):
        pprint(self.stats)

    @staticmethod
    def remove_plaintext(code: str):
        no_plaintext = code.splitlines()
        fix = copy.deepcopy(no_plaintext)
        for num, line in enumerate(no_plaintext):
            if line.strip() != "":
                try:
                    newline = line.strip()
                    ast.parse(newline, mode='single')
                except Exception as e:
                    if e.args[0] != "unexpected EOF while parsing":
                        fix[num] = None
        return "\n".join(filter(None, fix))

    @staticmethod
    def debug_mode(mode=False):  # Sets debug mode on or off
        return mode


class ASTIterator(ast.NodeVisitor):
    # Class for traversing the AST tree.
    def __init__(self):
        self.stats = {"import": [], "from": []}

    # (found online) finds the import packages and appends to
    # stats attribute of ASTFormer.
    def visit_import(self, node):
        for alias in node.names:
            self.stats["import"].append(alias.name)
        self.generic_visit(node)

    # (found online) finds the from imports and appends to
    # stats attribute of ASTFormer.
    def visit_import_from(self, node):
        for alias in node.names:
            self.stats["from"].append(alias.name)
        self.generic_visit(node)
