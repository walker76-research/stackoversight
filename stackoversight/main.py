import pickle

from stackoversight.scraper import Scraper
from stackoversight.trie import TrieNode, add


# SITE = StackAPI('stackoverflow')
# SITE.max_pages = 1
# SITE.pagesize = 100
# questions = SITE.fetch('questions', tagged="python")
with open("data/gitdump.pickle", "rb") as handle: # Opens the file
    questions = pickle.load(handle)
print("Retrieved questions")
# pick = Picklizer(questions)   # <- This is where we saved questions to file gitdump.pickle.

urls = [question['link'] for question in questions['items']]
print("Constructed urls")

scraper = Scraper()
soup_dict = {}
for url in urls[:10]:
    print(f'Scraping {url}')
    scraper.set_url(url)
    soup = scraper.scrape()
    code_snippets = soup.find_all('code')
    soup_dict[url] = code_snippets

root = TrieNode("*")

for key in soup_dict:
    value = soup_dict[key]
    for code_snippet in value:
        code = code_snippet.text
        print(code)
