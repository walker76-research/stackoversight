import pprint
from stackapi import StackAPI
from scraper import Scraper
import tokenize
import io


SITE = StackAPI('stackoverflow')
SITE.max_pages = 2
SITE.pagesize = 100
questions = SITE.fetch('questions', min=10)
print("Retrieved questions")

urls = []
for question in questions['items']:
    # pprint.pprint(question)
    if "tags" in question:
        tags = question['tags']
        for tag in tags:
            if tag == "python":
                urls.append(question['link'])
print("Constructed urls")

scraper = Scraper()
soup_dict = {}
for url in urls[:10]:
    scraper.set_url(url)
    soup = scraper.scrape()
    code_snippets = soup.find_all('code')
    soup_dict[url] = code_snippets

for key in soup_dict:
    value = soup_dict[key]
    for code_snippet in value:
        code = code_snippet.text
        f = io.StringIO(code)
        tokens = tokenize.tokenize(f.readline)
        pprint.pprint(tokens)
