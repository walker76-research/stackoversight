import keyword
from stackoversight.pipeline import ProcessingStep
from token import *


class KeywordExtractor(ProcessingStep):
    """
    Input for Pipeline - An array of arrays of tokens
    Output for Pipeline - An array of arrays of keywords
    """

    def operation(self, item):
        """
        Returns an array of keywords for an array of strings
        """

        # Setup an initial start token since there is no previous token
        prev_token = "START"
        keywords = []
        for token in item:

            # Ignore newlines since they're not important
            if token[0] == NEWLINE:
                continue

            # Retrieve the token and reset the previous token
            prev_token = get_keyword(prev_token, token)
            keywords.append(prev_token)

        return keywords


def get_keyword(prev_token, token):

    token_type = token[0]
    word = token[1]

    keywords = get_keywords()
    type_dictionary = get_type_dictionary()

    if word in keywords:
        return keywords[word]

    if token_type in type_dictionary:
        return type_dictionary[token_type]

    if token_type == NAME:
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

    if token_type == NUMBER:
        if prev_token == "KEYWORD_OPEN_PARENTHESIS" or prev_token == "KEYWORD_PARAMETER_SEPARATOR":
            return "KEYWORD_PARAMETER"

        return "NUMBER"

    if token_type == OP:

        if prev_token == "KEYWORD_PARAMETER":
            return "KEYWORD_PARAMETER_SEPARATOR"

        return "OPERATOR"


def get_keywords():
    keywords = {}
    for key in keyword.kwlist:
        keywords[key] = "KEYWORD_" + key.upper()
    keywords["range"] = "FUNCTION_RANGE"
    keywords["print"] = "FUNCTION_PRINT"
    keywords[":"] = "OPERATOR_COLON"
    keywords["("] = "KEYWORD_OPEN_PARENTHESIS"
    keywords[")"] = "KEYWORD_CLOSE_PARENTHESIS"
    return keywords


def get_type_dictionary():
    return {
        0: "FORMAT_ENDMARKER",
        3: "STRING",
        5: "INDENT",
        6: "DEDENT"
    }
