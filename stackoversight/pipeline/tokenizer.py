from io import StringIO
from tokenize import generate_tokens
from stackoversight.pipeline.filter import Filter


# This will receive a piece of code and should return an array of tokens
class Tokenizer(Filter):

    def operation(self, item):
        """
        Retrieves the tokens for a string representation of the code
        """
        return [(token[0], token[1]) for token in generate_tokens(StringIO(item).readline)]
