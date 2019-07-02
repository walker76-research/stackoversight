from stackapi import StackAPI
from scraper import Scraper
from tokenize import generate_tokens
from io import StringIO
from keyword_analyzer import KeywordAnalyzer
from trie import TrieNode, add, find_prefix
from astformer import ASTFormer, ASTFStatus
from gitpickler import Picklizer
from sanitizecode import SanitizeCode
import pickle


def get_keywords(code: str):
    keyword_analyzer = KeywordAnalyzer()
    tokens = []
    for token in generate_tokens(StringIO(code).readline):
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

    return keywords


# SITE = StackAPI('stackoverflow')
# SITE.max_pages = 1
# SITE.pagesize = 100
# questions = SITE.fetch('questions', tagged="python")
with open("gitdump.pickle", "rb") as handle: # Opens the file
    questions = pickle.load(handle)
print("Retrieved questions")
# pick = Picklizer(questions)   # <- This is where we saved questions to file gitdump.pickle.

urls = [question['link'] for question in questions['items']]
print("Constructed urls")

scraper = Scraper()
soup_dict = {}
for url in urls[:10]:
    scraper.set_url(url)
    soup = scraper.scrape()
    code_snippets = soup.find_all('code')
    soup_dict[url] = code_snippets

root = TrieNode("*")
code_issues = 0
code_totals = 0
for key in soup_dict:
    value = soup_dict[key]
    for code_snippet in value:
        code = code_snippet.text
        astf = ASTFormer(code)
        if astf.status == ASTFStatus.SUCCESS:
            keywords = get_keywords(code)
            add(root, keywords)
        else:
            sanitized_code = SanitizeCode(code)  # Attempt to sanitize the code
            astf2 = ASTFormer(sanitized_code)
            print(astf2.status)
            if astf2.status == ASTFStatus.FAILURE:  # Check if attempted fixes could verify python 2
                code_issues = code_issues + 1
            else:
                keywords = get_keywords(code)
                add(root, keywords)

print(str(code_totals) + " code snippets found. " + str(code_issues) + " could not compile.")
