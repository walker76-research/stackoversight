from pipeline.sanitizer import Sanitizer
from pipeline.filter import Filter
from pipeline.keyword_extractor import KeywordExtractor
from pipeline.tokenizer import Tokenizer
from pipeline.pipelineobject import Pipeline

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

code_samplet = """for i in len(array):
    k = 12
    j = 10
    for n in range(1, len(array) + i):
        j *= n
        k = k + i
    other_func_call()
    print('{}! = {}'.format(i,n))
    print('Done!')
"""

code_samplet2 = """def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y
    return matrix
"""

not_code = "This is an example of\nsomething that is not even a code snippet!\n" \
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
DEDENT
FORMAT_ENDMARKER
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
keywords = pipeline.feed([code_base, code_sample, code_samplet, code_samplet2, not_code])
keywords.set_input(code_sample)
keywords.form_lsh()
keywords.query(keywords[0])
print(keywords.get_results())