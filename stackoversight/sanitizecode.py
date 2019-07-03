from lib2to3 import refactor, fixes
from setuptools import lib2to3_fixer_packages
import lib2to3.main
import lib2to3.fixer_base


# Currently does not fully work. Was working for simple 'print x' to 'print(x)', need to investigate other fixes
# Should not need to ever be handled in main. Used as backend for astformer.py
class SanitizeCode:
    def __init__(self, code, error=None):
        self.error = error
        self.code = code

    def num_ws(self, line):
        ws = len(line.lstrip("\t"))
        if ws == len(line):
            ws = len(line.lstrip())
        return len(line) - ws

    def clean_false_indents(self):
        code = self.code.splitlines()
        flagged = False
        for num, line in enumerate(code):
            if not line.endswith(':') or flagged:
                if num + 1 < len(code):  # if there are more lines to check
                    ws_cur = self.num_ws(line)  # how many tabs are there preceding colon line
                    ws_nex = self.num_ws(code[num + 1])
                    if ws_nex > ws_cur:
                        remove_num = ws_nex - ws_cur
                        new_code = code[num + 1][remove_num:]
                        code[num + 1] = new_code
                        flagged = True
            else:
                flagged = False
        self.code = "\n".join(code)

    # Get the exact error types and sanitize from there
    def refactor(self):
        try:
            factory = refactor.RefactoringTool(refactor.get_fixers_from_package(lib2to3_fixer_packages[0]))
            return factory.refactor_string(self.code, "test code")
        except Exception as e:
            print(getattr(e, "message", repr(e)))
            return "print invalid"
