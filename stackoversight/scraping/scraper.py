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
from stackoversight.scraping.queue_monitor import QueueMonitor


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

        self.code_lock = threading.Lock()
        self.text_lock = threading.Lock()

    def __del__(self):
        for file_handle in self.file_handles:
            file_handle.close()

        for thread_handle in self.thread_handles:
            thread_handle.exit()
            # thread_handle.join()

    def start(self, parent_link_queue: Queue):
        code_io_handle = open('code.txt', 'w')
        text_io_handle = open('text.txt', 'w')

        self.file_handles.extend((code_io_handle, text_io_handle))

        child_link_queue = Queue()

        parent_link_thread = threading.Thread(target=self.scrape_parent_links,
                                              args=(parent_link_queue, self.site, child_link_queue))
        parent_link_thread.setName("StackExchange API Handler n")

        child_link_thread = threading.Thread(target=self.scrape_child_links,
                                             args=(child_link_queue, self.site, code_io_handle, text_io_handle))
        child_link_thread.setName("StackOverflow Scraping Handler n")

        queue_monitor = QueueMonitor(parent_link_queue)

        parent_link_thread.start()
        child_link_thread.start()
        queue_monitor.start()

        self.thread_handles.extend((parent_link_thread, child_link_thread, queue_monitor))

        flag = False
        while not flag:
            sleep(1)

            for handle in self.thread_handles:
                print(f'{handle.getName()} is {["not "] if [not handle.is_alive()] else [""]} healthy.')

                if not handle.is_alive():
                    flag = True
                    break

        if queue_monitor.is_alive():
            print(f'Since a thread has failed, this process will now terminate...')
        else:
            print(f'All links in parent queue processed, now terminating...')
        sleep(1)
        queue_monitor.join()  # to cleanup the thread

    def scrape_parent_links(self, input_queue: Queue, site: StackOverflow, output_queue: Queue):
        while True:
            if not input_queue.empty():
                link = input_queue.get()
                print(link)

                # TODO: thread this point on in this method for each parent link
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

                input_queue.task_done()

    def scrape_child_links(self, input_queue: Queue, site: StackOverflow, code_io_handle, text_io_handle):
        # for debug purposes
        while True:
            if not input_queue.empty():
                link = input_queue.get()
                print(link)

                # TODO: thread this point on in this method for each link
                # TODO: handle None response
                try:
                    response = site.process_request(link, pause=True)[0]
                except:
                    break

                for code in site.get_code(response):
                    with self.code_lock:
                        code_io_handle.write(code)

                for text in site.get_text(response):
                    with self.text_lock:
                        text_io_handle.write(text)

                input_queue.task_done()


# for debugging only
keys = ['RGaU7lYPN8L5KbnIfkxmGQ((', '1yfsxJa1AC*GlxN6RSemCQ((']

python_posts = StackOverflow.create_parent_link(sort=StackOverflow.Sorts.votes.value,
                                                order=StackOverflow.Orders.descending.value,
                                                tag=StackOverflow.Tags.python.value, page_size=100)

link_queue = Queue()
link_queue.put(python_posts)
link_queue.task_done()

scraper = StackOversight(keys)
scraper.start(link_queue)
