from pprint import pprint
from stackoversight.keyword_analyzer import KeywordAnalyzer
from stackoversight.pipeline import Pipeline, KeywordExtractor, Tokenizer

keyword_analyzer = KeywordAnalyzer()
code_base = "for i in range(1,11):\n" \
        "   n = 1\n" \
        "   for j in range(1, i+1):\n" \
        "       n *= j\n" \
        "   print('{}! = {}'.format(i, n))"

code_sample = "for i in range(25,100):\n" \
        "   n = 3\n" \
        "   for j in range(2, i+5):\n" \
        "       n *= j\n" \
        "   print('{}! = {}'.format(i, n))"

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
    Tokenizer(),
    KeywordExtractor()
]
pipeline = Pipeline()
pipeline.set_steps(processing_steps)
keywords = pipeline.feed([code_base, code_sample])

for keyword_arr in keywords:
    pprint(keyword_arr)
