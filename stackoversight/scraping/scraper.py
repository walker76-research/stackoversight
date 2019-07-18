# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.stack_overflow import StackOverflow
# For child link queue
from queue import Queue
# For threading the scraping process
import threading


def scrape_parent_link(url: str, site: StackOverflow, queue: Queue):
    while True:
        links = site.get_child_links(url, pause=True)
        has_more = links[1]
        links = links[0]

        list(map(queue.put, links))

        if not has_more:
            break


# address of the proxy server
proxy = 'http://localhost:5050'

# set the environment variable http_proxy and such
# os.environ['http_proxy'] = proxy
# os.environ['HTTP_PROXY'] = proxy
# os.environ['https_proxy'] = proxy
# os.environ['HTTPS_PROXY'] = proxy

client_keys = ['RGaU7lYPN8L5KbnIfkxmGQ((', 'RGaU7lYPN8L5KbnIfkxmGQ((']
stack_overflow = StackOverflow(client_keys)

python_posts = stack_overflow.create_parent_link(sort=stack_overflow.Sorts.votes.value,
                                                 order=stack_overflow.Orders.descending.value,
                                                 tag=stack_overflow.Tags.python.value, page_size=100)

print(python_posts)

link_queue = Queue()
threading.Thread(target=scrape_parent_link, args=(python_posts, stack_overflow, link_queue))

# for debug purposes
while True:
    if not link_queue.empty():
        link = link_queue.get()
        print(link)

        response = stack_overflow.process_request(link, pause=True)[0]

        for code in stack_overflow.get_code(response):
            # pickle the code
            print(code)

        for text in stack_overflow.get_text(response):
            # pickle the text
            print(text)

    print(stack_overflow.balancer.heap)
