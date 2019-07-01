import pprint
from stackapi import StackAPI, StackAPIError
from scraper import Scraper

SITE = StackAPI('stackoverflow')
SITE.max_pages = 2
SITE.page_size = 100
questions = SITE.fetch('questions', min=10)
print("Retrieved questions")

urls = []
for question in questions['items']:
    # pprint.pprint(question)
    urls.append(question['link'])
print("Constructed urls")

scraper = Scraper()
soup_dict = {}
for url in urls[:10]:
    scraper.set_url(url)
    soup = scraper.scrape()
    code_snippets = soup.find_all('code')
    soup_dict[url] = code_snippets

pprint.pprint(soup_dict)
