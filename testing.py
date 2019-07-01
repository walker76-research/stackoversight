import io
from io import StringIO
from tokenize import generate_tokens
import pprint

code = "import tokenize \nimport io\nclass _CHAIN(object):\n    def __init__(self, execution_context=None):\n       self.execution_context = execution_context\n    def eat(self, toktype, tokval, rowcol, line, logical_line):\n       #some code and error checking" \
        "print(toktype, tokval, rowcol, line, logical_line)"

f = io.StringIO(code)
for token in generate_tokens(StringIO(code).readline):
    pprint.pprint(token)
