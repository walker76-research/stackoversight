# Credit to Ben Shaver for his guide on scraping stackoverflow

# To send out HTTP requests
import requests
# To parse the HTML documents
from bs4 import BeautifulSoup
# To set the http_proxy environment variable
import os
# Use regex to filter links
import re
# For timing to avoid rate limiting
from random import randint
from time import sleep
# For StackOverflow info
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

python_posts = create_stackoverflow_parent_link(StackOverflowCategories.question,
                                                {StackOverflowTags.python},
                                                StackOverflowTabs.frequent)

print(python_posts)

child_links = get_child_links(python_posts)

# for debug purposes
for question in child_links:
    for code in get_code(question):
        print(code)

    for text in get_text(question):
        print(text)
