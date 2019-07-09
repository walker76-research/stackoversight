# Credit to Ben Shaver for his guide on scraping stackoverflow

# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.site.Site import *

# address of the proxy server
proxy = 'http://localhost:5050'
# number of posts
max_page = 1
# number of questions to grab
page_size = 1000

# set the environment variable http_proxy and such
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

client_ids = {15696, 15697}
site = StackOverflow(client_ids)

python_posts = site.create_parent_link(site.Categories.question, site.Tags.python, site.Tabs.frequent)

print(python_posts)

child_links = site.get_child_links(python_posts)

# for debug purposes
for question in child_links:
    for code in site.get_code(question):
        print(code)

    for text in site.get_text(question):
        print(text)
