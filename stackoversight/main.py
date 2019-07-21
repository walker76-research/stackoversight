import pickle
from pprint import pprint

from stackoversight.scraper import Scraper
from stackoversight.trie import TrieNode, add
from stackoversight.pipeline import Pipeline, Tokenizer, KeywordExtractor, Sanitizer, Filter


# SITE = StackAPI('stackoverflow')
# SITE.max_pages = 1
# SITE.pagesize = 100
# questions = SITE.fetch('questions', tagged="python")
with open("C:\Programs\code-duplication\data\gitdump.pickle", "rb") as handle: # Opens the file
    questions = pickle.load(handle)
print("Retrieved questions")
# pick = Picklizer(questions)   # <- This is where we saved questions to file gitdump.pickle.

urls = [question['link'] for question in questions['items']]
print("Constructed urls")
scraper = Scraper()

snippets = []
for url in urls[:2]:
    print(f'Scraping {url}')
    scraper.set_url(url)
    soup = scraper.scrape()
    code_snippets = soup.find_all('code')
    for code_snippet in code_snippets:
        snippets.append(code_snippet.text)

root = TrieNode("*")

pipeline = Pipeline([
    Sanitizer(),
    Filter(),
    Tokenizer(),
    KeywordExtractor()
])

result = pipeline.feed(snippets)
pprint(result)
