# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.stack_overflow import StackOverflow

# address of the proxy server
proxy = 'http://localhost:5050'

# set the environment variable http_proxy and such
# os.environ['http_proxy'] = proxy
# os.environ['HTTP_PROXY'] = proxy
# os.environ['https_proxy'] = proxy
# os.environ['HTTPS_PROXY'] = proxy

client_keys = ['RGaU7lYPN8L5KbnIfkxmGQ((', 'RGaU7lYPN8L5KbnIfkxmGQ((']

site = StackOverflow(client_keys)

python_posts = site.create_parent_link(sort=site.Sorts.votes.value, order=site.Orders.descending.value,
                                       tag=site.Tags.python.value, page_size=100)

print(python_posts)

child_links = site.get_child_links(python_posts, pause=True)
has_more = child_links[1]
child_links = child_links[0]

# for debug purposes
for question in child_links:
    print(question)
    response = site.process_request(question, pause=True)[0]

    for code in site.get_code(response):
        print(code)

    for text in site.get_text(response):
        print(text)

print(site.balancer.heap)
