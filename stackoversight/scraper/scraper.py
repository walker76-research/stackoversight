# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraper.stack_overflow import StackOverflow
# For client_credential objects
from requests.auth import HTTPBasicAuth

# address of the proxy server
proxy = 'http://localhost:5050'

# set the environment variable http_proxy and such
# os.environ['http_proxy'] = proxy
# os.environ['HTTP_PROXY'] = proxy
# os.environ['https_proxy'] = proxy
# os.environ['HTTPS_PROXY'] = proxy

client_auths = [HTTPBasicAuth(15696, 'GmSeo*z3TFTDcL8wIz3xUA(('),
                HTTPBasicAuth(15697, '1DF6PpPTMTQOT*Mm8v*Mng((')]

site = StackOverflow(client_auths)

python_posts = site.create_parent_link(site.Categories.question, [site.Tags.python], site.Tabs.frequent)

print(python_posts)

child_links = site.get_child_links(python_posts, pause=True)

# for debug purposes
for question in child_links:
    print(question)
    soup = site.get_soup(question, pause=True)

    for code in site.get_code(soup):
        print(code)

    for text in site.get_text(soup):
        print(text)

print(site.balancer.heap)
