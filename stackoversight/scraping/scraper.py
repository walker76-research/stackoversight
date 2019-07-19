# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.stack_overflow import StackOverflow
# For child link queue
from queue import Queue
# For threading the scraping process
import threading


def scrape_parent_link(input_queue: Queue, site: StackOverflow, output_queue: Queue):
    while True:
        if not input_queue.empty():
            link = input_queue.get()
            print(link)

            while True:
                try:
                    # TODO: handle None response
                    links = site.get_child_links(link, pause=True)
                except:
                    print("Exception caught in scrape_parent_link thread, ending process...")
                    break
                    # terminate

                has_more = links[1]
                links = links[0]

                list(map(output_queue.put, links))

                if not has_more:
                    break


def scrape_child_link(input_queue: Queue, site: StackOverflow):
    # for debug purposes
    while True:
        if not input_queue.empty():
            link = input_queue.get()
            print(link)

            try:
                # TODO: handle None response
                response = site.process_request(link, pause=True)[0]
            except:
                print('Exception caught in scrape_child_link thread, ending process...')
                break
                # terminate

            for code in site.get_code(response):
                # pickle the code
                print(code)

            for text in site.get_text(response):
                # pickle the text
                print(text)


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

parent_link_queue = Queue()
child_link_queue = Queue()

parent_link_queue.put(python_posts)

parent_link_thread = threading.Thread(target=scrape_parent_link, args=(parent_link_queue, stack_overflow,
                                                                       child_link_queue))
child_link_thread = threading.Thread(target=scrape_child_link, args=(child_link_queue, stack_overflow))

parent_link_thread.start()
child_link_thread.start()
