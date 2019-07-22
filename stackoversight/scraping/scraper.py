# To set the http_proxy environment variable
import os
# For making the site requests and overall request management
from stackoversight.scraping.stack_overflow import StackOverflow
# For child link queue
from queue import Queue
# For threading the scraping process
import threading
# For raising error
import ctypes


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

    def start(self, parent_link_queue: Queue, code_file_name='code.txt', text_file_name='text.txt'):
        code_io_handle = open(code_file_name, 'w')
        text_io_handle = open(text_file_name, 'w')

        self.file_handles.extend((code_io_handle, text_io_handle))

        child_link_queue = Queue()

        kill = threading.Event()

        parent_link_thread = threading.Thread(target=self.thread_executioner,
                                              args=(parent_link_queue, self.site, child_link_queue, kill))
        parent_link_thread.setName("StackExchange API Manager")

        child_link_thread = threading.Thread(target=self.scrape_child_links,
                                             args=(child_link_queue, self.site, code_io_handle, text_io_handle, kill))
        child_link_thread.setName("StackOverflow Scraping Manager")

        self.thread_handles.extend((parent_link_thread, child_link_thread))

        for handle in self.thread_handles:
            handle.start()

        kill.wait()
        for handle in self.thread_handles:
            alive = handle.is_alive()
            print(f'{handle.getName()} is {["not "] if [not alive] else [""]} healthy.')

            if alive:
                if not ctypes.pythonapi.PyThreadState_SetAsyncExc(handle, ctypes.py_object(SystemExit)):
                    raise ChildProcessError
            handle.join()

        for file_handle in self.file_handles:
            file_handle.close()

    @staticmethod
    def mass_murder(victims: Queue):
        try:
            while True:
                victim = victims.get(block=True)
                StackOversight.murder(victim)
        except SystemExit:
            # logging

    @staticmethod
    def murder(victim: threading.Thread):
        alive = victim.is_alive()
        if alive:
            if not ctypes.pythonapi.PyThreadState_SetAsyncExc(victim, ctypes.py_object(SystemExit)):
                raise ChildProcessError
        victim.join()

    @staticmethod
    def thread_executioner(target, input_queue: Queue, *args):
        hit_queue = Queue()
        thread_killer = threading.Thread(target=StackOversight.mass_murder, args=[hit_queue], daemon=True)
        thread_killer.start()

        try:
            while True:
                next_in = input_queue.get(block=True)
                print(next_in)

                threading.Thread(target=target, args=(next_in, *args), daemon=True)

        except SystemExit:
            StackOversight.murder(thread_killer)
            print('Done scraping parent links')

    def scrape_parent_links(self, input_queue: Queue, site: StackOverflow, output_queue: Queue, failure: threading.Event):
        StackOversight.thread_executioner(site, output_queue, failure, target=StackOversight.scrape_parent_link, input_queue=input_queue)

    def scrape_child_links(self, input_queue: Queue, site: StackOverflow, code_io_handle, text_io_handle,
                           failure: threading.Event):
        try:
            while True:
                link = input_queue.get(block=True)
                print(link)

                # TODO: thread this point on in this method for each link
                # TODO: handle None response
                try:
                    response = site.process_request(link, pause=True)[0]
                except SystemExit:
                    raise
                except:
                    # TODO: logging
                    failure.set()
                    raise

                for code in site.get_code(response):
                    with self.code_lock:
                        code_io_handle.write(code)

                for text in site.get_text(response):
                    with self.text_lock:
                        text_io_handle.write(text)

        except SystemExit:
            print('Done scraping child links')

    @staticmethod
    def scrape_parent_link(link: str, site: StackOverflow, output_queue: Queue, failure: threading.Event,
                           used_parents: Queue):
        try:
            while True:
                try:
                    # TODO: handle None response
                    # TODO: make sure actually incrementing page
                    links = site.get_child_links(link, pause=True)
                except SystemExit:
                    raise
                except:
                    # TODO: logging
                    failure.set()
                    raise

                has_more = links[1]
                links = links[0]
                list(map(output_queue.put, links))

                if not has_more:
                    used_parents.put(threading.currentThread())
                    break
        except SystemExit:
            # logging


# for debugging only
keys = ['RGaU7lYPN8L5KbnIfkxmGQ((', '1yfsxJa1AC*GlxN6RSemCQ((']

python_posts = StackOverflow.create_parent_link(sort=StackOverflow.Sorts.votes.value,
                                                order=StackOverflow.Orders.descending.value,
                                                tag=StackOverflow.Tags.python.value, page_size=100)

link_queue = Queue()
link_queue.put(python_posts)

scraper = StackOversight(keys)
scraper.start(link_queue)
