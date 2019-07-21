# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.stack_overflow import StackOverflow
# For child link queue
from queue import Queue
# For threading the scraping process
import threading
# Reduce busy wait
from time import sleep


def scrape_parent_links(input_queue: Queue, site: StackOverflow, output_queue: Queue):
    while True:
        if not input_queue.empty():
            link = input_queue.get()
            print(link)

            while True:
                # TODO: handle None response
                try:
                    links = site.get_child_links(link, pause=True)
                except:
                    break

                has_more = links[1]
                links = links[0]

                list(map(output_queue.put, links))

                if not has_more:
                    break


def scrape_child_links(input_queue: Queue, site: StackOverflow, code_io_handle, text_io_handle):
    # for debug purposes
    while True:
        if not input_queue.empty():
            link = input_queue.get()
            # print(link)

            # TODO: handle None response
            try:
                response = site.process_request(link, pause=True)[0]
            except:
                break

            for code in site.get_code(response):
                code_io_handle.write(code)
                # print(code)

            for text in site.get_text(response):
                text_io_handle.write(code)
                # print(text)


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

    def start(self, parent_link_queue: Queue):
        code_io_handle = open('code.txt', 'w')
        text_io_handle = open('text.txt', 'w')

        self.file_handles.extend((code_io_handle, text_io_handle))

        child_link_queue = Queue()

        parent_link_thread = threading.Thread(target=scrape_parent_links,
                                              args=(parent_link_queue, self.site, child_link_queue))
        parent_link_thread.setName("StackExchange API Handler")

        child_link_thread = threading.Thread(target=scrape_child_links,
                                             args=(child_link_queue, self.site, code_io_handle, text_io_handle))
        child_link_thread.setName("StackOverflow Scraping Handler")

        parent_link_thread.start()
        child_link_thread.start()

        while all([handle.is_alive() for handle in self.thread_handles]):
            print('All threads healthy...')
            sleep(5)

        self.terminate()

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

scraper = StackOversight(keys)
scraper.start(link_queue)
