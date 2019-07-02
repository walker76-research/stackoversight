import keyword

class KeywordAnalyzer:

    def __init__(self):
        self.keyword = None
        self.keywords = {}
        for kywd in keyword.kwlist:
            self.keywords[kywd] = "KEYWORD_" + kywd.upper()
        self.keywords["range"] = "FUNCTION_RANGE"
        self.keywords["print"] = "FUNCTION_PRINT"
        self.keywords[":"] = "OPERATOR_COLON"

    def is_keyword(self, token, prev_token):
        type = token[0]
        word = token[1]

        if word in self.keywords:
            self.keyword = self.keywords[word]
            return True

        if type == 0:
            self.keyword = "FORMAT_ENDMARKER"
            return True

        if type == 5:
            self.keyword = "INDENT"
            return True

        if type == 6:
            self.keyword = "DEDENT"
            return True

        if prev_token == "KEYWORD_IMPORT" and type == 1:
            self.keyword = "KEYWORD_MODULE"
            return True

        if prev_token == "KEYWORD_CLASS" and type == 1:
            self.keyword = "KEYWORD_CLASS_NAME"
            return True

        if type == 2:
            if prev_token == "KEYWORD_OPEN_PARENTHESIS" or prev_token == "KEYWORD_PARAMETER_SEPARATOR":
                self.keyword = "KEYWORD_PARAMETER"
                return True
            else:
                self.keyword = "NUMBER"
                return True

        if prev_token == "KEYWORD_OPEN_PARENTHESIS" or prev_token == "KEYWORD_PARAMETER_SEPARATOR"\
                and type == 1:
            self.keyword = "KEYWORD_PARAMETER"
            return True

        if prev_token == "KEYWORD_DEF" and type == 1:
            self.keyword = "KEYWORD_FUNCTION_NAME"
            return True

        if prev_token == "KEYWORD_FOR" and type == 1:
            self.keyword = "VARIABLE"
            return True

        if type == 53:
            if prev_token == "KEYWORD_PARAMETER":
                self.keyword = "KEYWORD_PARAMETER_SEPARATOR"
                return True

            if word == "(":
                self.keyword = "KEYWORD_OPEN_PARENTHESIS"
                return True

            if word == ")":
                self.keyword = "KEYWORD_CLOSE_PARENTHESIS"
                return True

            self.keyword = "OPERATOR"
            return True

        return False

    def get_keyword(self):
        return self.keyword
