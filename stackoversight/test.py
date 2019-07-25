from pipeline.sanitizer import Sanitizer
from pipeline.filter import Filter
from pipeline.keyword_extractor import KeywordExtractor
from pipeline.tokenizer import Tokenizer
from pipeline.pipelineobject import Pipeline
import json
import asyncio
import rq

# TODO: tuples instead

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

# Set the pipeline steps up into the correct order
processing_steps = [
    Sanitizer(),
    Filter(),
    Tokenizer(),
    KeywordExtractor()
]

snippets = [
    code_base,
    code_sample,
    code_samplet,
    code_samplet2,
    not_code
]

pipeline = Pipeline(processing_steps)
output = pipeline.execute_synchronous(snippets)
output.form_lsh()
output.set_input(output[0])
query_out = output.query()

result = query_out.get()

print(result)
print(query_out.get_snippet(0))
print(query_out.message)
