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
    MAX_ITERATIONS = 25

    def __init__(self, source):
        self.code = source
        self.status = ASTFStatus.PROCESSING
        self.faulty_line = -1
        self.iterations = 0
        self.tree = None

        # Make sure the code runs (filter)
        while self.status is not ASTFStatus.SUCCESS and self.iterations < ASTFormer.MAX_ITERATIONS:
            self.cleanup()
            self.iterations = self.iterations + 1
        if self.debug_mode():
            if self.status == ASTFStatus.SUCCESS:
                print("AST Formed Successfully, resolved " + str(self.iterations) + " errors.")
                print(self.code)
            else:
                print("Could not form AST.")

    def cleanup(self):
        try:
            self.tree = ast.parse(str(self.code))
            self.status = ASTFStatus.SUCCESS
        except IndentationError as e:                               # TODO: handle more types of exceptions and sanitize as needed
            if e.args[0] == "unexpected indent":
                san_code = SanitizeCode(self.code)
                san_code.remove_false_indents()
                self.code = san_code.code
                try:
                    self.tree = ast.parse(self.code)
                    self.status = ASTFStatus.SUCCESS
                except Exception as e:
                    self.status = ASTFStatus.FAILURE
                    if self.debug_mode():
                        self.debug_exception(e)
            elif e.args[0] == "expected an indented block":
                san_code = SanitizeCode(self.code)
                san_code.add_indents(e.args[1][1]-1)
                self.code = san_code.code
                try:
                    self.tree = ast.parse(self.code)
                    self.status = ASTFStatus.SUCCESS
                except Exception as e:
                    self.status = ASTFStatus.FAILURE
                    if self.debug_mode():
                        self.debug_exception(e)
        except SyntaxError as e:
            self.tree = None
            self.status = ASTFStatus.FAILURE
            if self.debug_mode():
                self.debug_exception(e)

    def debug_exception(self, e):
        pprint("Failed to create syntax tree. Cannot compile the code to Python.")
        pprint(self.code)
        print(getattr(e, 'message', repr(e)))
        self.faulty_line = e.lineno

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
    def debug_mode(mode=False):  # Sets debug mode on or off
        return mode
