from io import StringIO
from tokenize import generate_tokens
from pprint import pprint
from stackoversight.keyword_analyzer import KeywordAnalyzer
from stackoversight.trie import TrieNode, add, find_prefix

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
    """
    Retrieves the tokens for a string representation of the code
    """

    tokens = []

    # Print all the tokens
    for token in generate_tokens(StringIO(code).readline):
        pprint(token)
        tokens.append((token[0], token[1]))

    return tokens


def get_keywords(tokens: []):
    """
    Retrieves the keyword representation of an array of tokens
    """

    # Setup an initial start token since there is no previous token
    prev_token = "START"
    keywords = []
    for token in tokens:

        # Ignore newlines since they're not important
        if token[0] == 4:
            continue

        # Retrieve the token and reset the previous token
        prev_token = keyword_analyzer.get_keyword(prev_token, token)
        keywords.append(prev_token)

    return keywords


base_tokens = get_tokens(code_base)
testing_tokens = get_tokens(code_sample)

pprint(base_tokens)
root = TrieNode('*')
add(root, base_tokens)

print(find_prefix(root, testing_tokens))