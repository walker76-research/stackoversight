from io import StringIO
from tokenize import generate_tokens
from pipeline.processing_step import ProcessingStep


class Tokenizer(ProcessingStep):
    """
    Input for Pipeline - An array of strings, each string is a code snippet
    Output for Pipeline - An array of arrays of tokens
    """

    def operation(self, item):
        """
        Returns the tokens for a string representation of the code
        """
        return [(token[0], token[1]) for token in generate_tokens(StringIO(item).readline)]

    @property
    def name(self):
        return "tokenizer"
