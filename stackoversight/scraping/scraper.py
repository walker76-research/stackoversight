# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.stack_overflow import StackOverflow
# For child link queue
from queue import Queue
# For threading the scraping process
import threading
# For io
from io import IOBase


def scrape_parent_links(input_queue: Queue, site: StackOverflow, output_queue: Queue):
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


def scrape_child_links(input_queue: Queue, site: StackOverflow, ostream):
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
                # use ostream
                print(code)

            for text in site.get_text(response):
                # use ostream
                print(text)


class StackOversight(object):
    def __init__(self, client_keys: list, proxy=None):
        if proxy:
            # address of the proxy server
            self.proxy = 'http://localhost:5050'

            # set the environment variable http_proxy and such
            os.environ['http_proxy'] = proxy
            os.environ['HTTP_PROXY'] = proxy
            os.environ['https_proxy'] = proxy
            os.environ['HTTPS_PROXY'] = proxy

        self.site = StackOverflow(client_keys)

        self.thread_handles = []
        self.file_handles = []

    def start(self, parent_link_queue: Queue, io: IOBase):
        code_file_handle = io.open('code.txt', 'w')
        text_file_handle = io.open('text.txt', 'w')

        self.file_handles.extend((code_file_handle, text_file_handle))

        child_link_queue = Queue()

        parent_link_thread = threading.Thread(target=scrape_parent_links,
                                              args=(parent_link_queue, self.site, child_link_queue))
        parent_link_thread.setName("StackExchange API Handler")

        child_link_thread = threading.Thread(target=scrape_child_links, args=(child_link_queue, self.site))
        child_link_thread.setName("StackOverflow Scraping Handler")

        parent_link_thread.start()
        child_link_thread.start()

    def terminate(self):
        for file_handle in self.file_handles:
            file_handle.close()

        for thread_handle in self.thread_handles:
            thread_handle.exit()


# for debugging only
keys = ['RGaU7lYPN8L5KbnIfkxmGQ((', 'RGaU7lYPN8L5KbnIfkxmGQ((']

python_posts = StackOverflow.create_parent_link(sort=StackOverflow.Sorts.votes.value,
                                                order=StackOverflow.Orders.descending.value,
                                                tag=StackOverflow.Tags.python.value, page_size=100)

link_queue = Queue()
link_queue.put(python_posts)
