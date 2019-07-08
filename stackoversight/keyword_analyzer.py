import keyword
from pprint import pprint


class KeywordAnalyzer:
    def __init__(self):
        self.keywords = {}
        for kywd in keyword.kwlist:
            self.keywords[kywd] = "KEYWORD_" + kywd.upper()
        self.keywords["range"] = "FUNCTION_RANGE"
        self.keywords["print"] = "FUNCTION_PRINT"
        self.keywords[":"] = "OPERATOR_COLON"

    def get_keyword(self, prev_token, token):
        type = token[0]
        word = token[1]

        if word in self.keywords:
            return self.keywords[word]

        if type == 0:
            return "FORMAT_ENDMARKER"

        if type == 1:
            if prev_token == "KEYWORD_IMPORT":
                return "KEYWORD_MODULE"

            if prev_token == "KEYWORD_CLASS":
                return "KEYWORD_CLASS_NAME"

            if prev_token == "KEYWORD_OPEN_PARENTHESIS" or prev_token == "KEYWORD_PARAMETER_SEPARATOR":
                return "KEYWORD_PARAMETER"

            if prev_token == "KEYWORD_DEF":
                return "KEYWORD_FUNCTION_NAME"

            if prev_token == "KEYWORD_FOR" or prev_token == "KEYWORD_WHILE":
                return "VARIABLE"

            return "VARIABLE"

        if type == 2:
            if prev_token == "KEYWORD_OPEN_PARENTHESIS" or prev_token == "KEYWORD_PARAMETER_SEPARATOR":
                return "KEYWORD_PARAMETER"
            else:
                return "NUMBER"

        if type == 3:
            return "STRING"

        if type == 5:
            return "INDENT"

        if type == 6:
            return "DEDENT"

        if type == 53:

            if word == "(":
                return "KEYWORD_OPEN_PARENTHESIS"

            if word == ")":
                return "KEYWORD_CLOSE_PARENTHESIS"

            if prev_token == "KEYWORD_PARAMETER":
                return "KEYWORD_PARAMETER_SEPARATOR"

            return "OPERATOR"

        pprint(token)