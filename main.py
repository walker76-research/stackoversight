import pprint
from stackapi import StackAPI, StackAPIError
from scraper import Scraper

SITE = StackAPI('stackoverflow')
comments = SITE.fetch('comments')

post_ids = []
for comment_metadata in comments["items"]:
    post_ids.append(comment_metadata['post_id'])

post_ids = post_ids[:20]
try:
    posts = SITE.fetch('posts', ids=post_ids)
except StackAPIError as e:
    print(e.message)
    exit(-1)

urls = []
for post_metadata in posts["items"]:
    urls.append(post_metadata['link'])

scraper = Scraper()
soup_dict = {}
for url in urls:
    scraper.set_url(url)
    soup = scraper.scrape()
    soup_dict[url] = soup

pprint.pprint(soup_dict)
