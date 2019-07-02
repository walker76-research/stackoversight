from lib2to3 import refactor, fixes
from setuptools import lib2to3_fixer_packages

#Currently does not fully work. Was working for simple 'print x' to 'print(x)', need to investigate other fixes
class SanitizeCode:

    def __init__(self, code):
        self.code = self.sanitize()

    def sanitize(self):
        try:
            words = str(self.code).split()
            factory = refactor.RefactoringTool(refactor.get_fixers_from_package(lib2to3_fixer_packages[0]))
            return factory.refactor_string(self.code, "test code")
        except Exception as e:
            print(getattr(e, name="message"))
            return "print invalid"
