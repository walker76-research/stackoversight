import ast
from enum import Enum
from stackoversight.pipeline.processing_step import ProcessingStep
from stackoversight.pipeline.sanitizer import Sanitizer


class Filter(ProcessingStep):
    """
    Input for Pipeline - An array of arrays of code snippet strings
    Output for Pipeline - An array of arrays of code snippet strings
    """

    def __init__(self):
        super(ProcessingStep, self).__init__()
        self.increments = 10
        self.max_increments = 10

    def operation(self, item):
        """
        Returns a code snippet that can actually be compiled. Sanitizes more as needed. None if not
        """
        item = self.check_filter(item)
        while self.increments > 1 and item is None:
            self.increments = self.increments - 1
            item = self.check_filter(item)
        self.increments = self.max_increments
        return item

    def check_filter(self, item):
        try:
            ast.parse(str(item))
            return item
        except IndentationError as e:
            return self.handle_indentations(item, e)
        except SyntaxError as e:
            return None

    @staticmethod
    def handle_indentations(item, e):
        if e.args[0] == "unexpected indent":
            item = Sanitizer.remove_false_indents(item)
            try:
                ast.parse(item)
                return item
            except Exception:
                return None
        elif e.args[0] == "expected an indented block":
            item = Sanitizer.add_indents(item, e.args[1][1] - 1)
            try:
                ast.parse(item)
                return item
            except Exception:
                return None
