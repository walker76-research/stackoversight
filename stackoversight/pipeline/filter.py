import ast
from enum import Enum
from stackoversight.pipeline.processing_step import ProcessingStep
from stackoversight.pipeline.sanitizer import Sanitizer


class Filter(ProcessingStep):
    """
    Input for Pipeline - An array of arrays of code snippet strings
    Output for Pipeline - An array of arrays of code snippet strings
    """
    class FilterStatus(Enum):
        SUCCESS = 0
        FAIL = 1

    def __init__(self):
        super(ProcessingStep, self).__init__()
        self.filter_status = Filter.FilterStatus.FAIL
        self.increments = 10
        self.max_increments = 10

    def operation(self, filter):
        """
        Returns a code snippet that can actually be compiled. Sanitizes more as needed. None if not
        """
        while self.increments > 1 or self.filter_status is Filter.FilterStatus.FAIL:
            self.increments = self.increments - 1
            filter = self.filter(filter)
        self.increments = self.max_increments
        return filter

    def filter(self, item):
        try:
            ast.parse(str(item))
            self.filter_status = Filter.FilterStatus.SUCCESS
        except IndentationError as e:
            if e.args[0] == "unexpected indent":
                item = Sanitizer.remove_false_indents(item)
                try:
                    ast.parse(item)
                    self.filter_status = Filter.FilterStatus.SUCCESS
                except Exception as e:
                    item = None
                    self.filter_status = Filter.FilterStatus.FAIL
            elif e.args[0] == "expected an indented block":
                item = Sanitizer.add_indents(item, e.args[1][1]-1)
                try:
                    ast.parse(item)
                    self.filter_status = Filter.FilterStatus.SUCCESS
                except Exception as e:
                    item = None
                    self.filter_status = Filter.FilterStatus.FAIL
        except SyntaxError as e:
            item = None
            self.filter_status = Filter.FilterStatus.FAIL
        finally:
            return item
