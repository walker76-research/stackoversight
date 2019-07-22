from pprint import pprint
from pipeline import Pipeline, KeywordExtractor, Tokenizer, Sanitizer, Filter

code_base = "for i in range(1,11):\n" \
        "   n = 1\n" \
        "   for j in range(1, i+1):\n" \
        "       n *= j\n" \
        "   print('{}! = {}'.format(i, n))"

code_sample = "for i in range(25,100):\n" \
        "   n = 3\n" \
        "   # This is a comment!\n" \
        "   # Notice how it is found as a 'NONE'!\n" \
        "   for j in range(2, i+5):\n" \
        "       n *= j\n" \
        "       # Another comment!\n" \
        "   print('{}! = {}'.format(i, n))"

not_code =  "This is an example of\nsomething that is not even a code snippet!\n" \
            " it contains code such as: for i in range(1, 10):\n" \
            " But it would never compile."

'''
KEYWORD_FOR
VARIABLE
KEYWORD_IN
FUNCTION
PARAMETER
PARAMETER
INDENT
VARIABLE
OPERATOR_ASSIGN
NUMBER
KEYWORD_FOR
VARIABLE
KEYWORD_IN
FUNCTION
PARAMETER
PARAMETER
INDENT
'''

processing_steps = [
    Sanitizer(),
    Filter(),
    Tokenizer(),
    KeywordExtractor()
]
pipeline = Pipeline()
pipeline.set_steps(processing_steps)
keywords = pipeline.feed([code_base, code_sample, not_code])

keywords.print()