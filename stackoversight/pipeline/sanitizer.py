import ast
import copy
from stackoversight.pipeline import ProcessingStep


class Sanitizer(ProcessingStep):
    """
    Input for Pipeline - An array of arrays of code snippet strings
    Output for Pipeline - An array of arrays of code snippet strings
    """
    def operation(self, item):
        """
        Returns a code snippet that is cleaned from comments/plaintext/bad indentation
        """
        item = self.remove_plaintext(item)
        item = self.remove_comments(item)
        item = self.remove_false_indents(item)
        return item

    @staticmethod
    def num_ws(line):
        ws = len(line.lstrip("\t"))
        if ws == len(line):
            ws = len(line.lstrip())
        return len(line) - ws

    @staticmethod
    def remove_comments(code):
        code = code.splitlines()
        for num, line in enumerate(code):
            comment = line.find("#")
            if comment > 0:
                if line[comment - 1] != "\\":
                    fixed_line = line[0:comment]
                    code[num] = fixed_line
        return "\n".join(code)

    @staticmethod
    def remove_plaintext(code):
        no_plaintext = code.splitlines()
        fix = copy.deepcopy(no_plaintext)
        for num, line in enumerate(no_plaintext):
            if not line.strip():
                try:
                    newline = line.strip()
                    ast.parse(newline, mode='single')
                except Exception as e:
                    if e.args[0] != "unexpected EOF while parsing":
                        fix[num] = None
        return "\n".join(filter(None, fix))

    @staticmethod
    def remove_false_indents(code):
        code = code.splitlines()
        flagged = False
        for num, line in enumerate(code):
            if not line.endswith(':') or flagged:
                if num + 1 < len(code):  # if there are more lines to check
                    ws_cur = Sanitizer.num_ws(line)  # how many tabs are there preceding colon line
                    ws_nex = Sanitizer.num_ws(code[num + 1])
                    if ws_nex > ws_cur:
                        remove_num = ws_nex - ws_cur
                        new_code = code[num + 1][remove_num:]
                        code[num + 1] = new_code
                        flagged = True
            else:
                flagged = False
        return "\n".join(code)

    @staticmethod
    def add_indents(code, lineno):
        code = code.splitlines()
        line = " " * 4 + code[lineno]
        code[lineno] = line
        return "\n".join(code)
