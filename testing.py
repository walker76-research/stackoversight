from io import StringIO
from tokenize import generate_tokens
import pprint
from keyword_analyzer import KeywordAnalyzer
from trie import TrieNode, add, find_prefix

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


def get_tokens(code: str):
    tokens = []
    for token in generate_tokens(StringIO(code_base).readline):
        # pprint.pprint(token)
        tokens.append((token[0], token[1]))

    start_token = "START"
    keywords = []
    for token in tokens:

        if token[1] == '\n':
            continue

        if keyword_analyzer.is_keyword(token, start_token):
            # pprint.pprint(keyword_analyzer.get_keyword())
            start_token = keyword_analyzer.get_keyword()
            keywords.append(start_token)

    return tokens


base_tokens = get_tokens(code_base)
testing_tokens = get_tokens(code_sample)

root = TrieNode('*')
add(root, base_tokens)

print(find_prefix(root, testing_tokens))
