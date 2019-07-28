import json
import logging
import os
import threading
import time
from queue import Queue

from stackoversight.scraping.stack_overflow import StackOverflow
from stackoversight.scraping.thread_executioner import ThreadExecutioner


class StackOversight(object):
    code_lock = threading.Lock()
    text_lock = threading.Lock()

    def __init__(self, client_keys: list, kill: threading.Event, proxy=None):
        if proxy:
            logging.info(f'Proxy {proxy} is being used.')

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

        self.kill = kill

    def start(self, parent_link_queue: Queue, code_file_name='code.txt', text_file_name='text.txt'):
        code_io_handle = open(code_file_name, 'w')
        text_io_handle = open(text_file_name, 'w')

        self.file_handles.extend((code_io_handle, text_io_handle))

        child_link_queue = Queue()

        parent_link_thread = threading.Thread(target=ThreadExecutioner.execute,
                                              args=(self.scrape_parent_link, parent_link_queue, self.site,
                                                    child_link_queue, self.kill))
        parent_link_thread.setName("StackExchange API Manager")

        child_link_thread = threading.Thread(target=ThreadExecutioner.execute,
                                             args=(self.scrape_child_link, child_link_queue, self.site, code_io_handle,
                                                   text_io_handle, self.kill))
        child_link_thread.setName("StackOverflow Scraping Manager")

        self.thread_handles.extend((parent_link_thread, child_link_thread))

        for handle in self.thread_handles:
            logging.info(f'Starting {handle.getName()}.')

            handle.start()

        self.kill.wait()

        for handle in self.thread_handles:
            was_alive = ThreadExecutioner.murder(handle)
            logging.debug(f'{handle.getName()} was {["not "] if [not was_alive] else [""]} alive.')

        for file_handle in self.file_handles:
            file_handle.close()

    @staticmethod
    def scrape_parent_link(link: str, used_parents: Queue, site: StackOverflow, output_queue: Queue,
                           kill: threading.Event):
        current_thread_name = threading.current_thread().getName()
        has_more = True
        response = None
        page = 1

        try:
            while has_more:
                try:
                    response = site.get_child_links(link + f'&{StackOverflow.fields["page"]}={page}', pause=True)
                except SystemExit:
                    raise
                except:
                    logging.critical(f'Unexpected error caught in {current_thread_name} after making'
                                     f'request with {link}.\n{[response] if [response] else ["Response not captured!"]}'
                                     f'\nNow ending process.')
                    kill.set()

                # TODO: handle None response
                has_more = response[1]
                response = response[0]
                list(map(output_queue.put, response))

                if not has_more:
                    logging.info(f'Finished with link {link}, now marking {current_thread_name} for death.')

                    used_parents.put(threading.currentThread())
                    break
                else:
                    page += 1

        except SystemExit:
            logging.info(f'System exit exception raised, {current_thread_name} successfully killed.')

    def scrape_child_link(self, link: str, used_children: Queue, site: StackOverflow, code_io_handle, text_io_handle,
                          kill: threading.Event):
        current_thread_name = threading.current_thread().getName()
        response = None

        try:
            try:
                response = site.process_request(link, pause=True)[0]
            except SystemExit:
                raise
            except:
                logging.critical(f'Unexpected error caught in {current_thread_name} after making'
                                 f'request with {link}.\n{[response] if [response] else ["Response not captured!"]}'
                                 f'\nNow ending process.')

                kill.set()

            # TODO: handle None response
            for code in site.get_code(response):
                snippet = {'snippet': code}

                with self.code_lock:
                    json.dump(snippet, code_io_handle)

            for text in site.get_text(response):
                snippet = {'snippet': text}

                with self.text_lock:
                    json.dump(snippet, text_io_handle)

            logging.info(f'Finished with link {link}, now marking {current_thread_name} for death.')
            used_children.put(threading.current_thread())

        except SystemExit:
            logging.info(f'System exit exception raised, {current_thread_name} successfully killed.')


# for debugging only
logging.basicConfig(filename=f'scraper.{time.strftime("%Y%m%d-%H%M%S")}.log', level=logging.DEBUG)

keys = ['RGaU7lYPN8L5KbnIfkxmGQ((', '1yfsxJa1AC*GlxN6RSemCQ((']

python_posts = StackOverflow.create_parent_link(sort=StackOverflow.Sorts.votes.value,
                                                order=StackOverflow.Orders.descending.value,
                                                tag=StackOverflow.Tags.python.value, page_size=100)

java_posts = StackOverflow.create_parent_link(sort=StackOverflow.Sorts.votes.value,
                                              order=StackOverflow.Orders.descending.value,
                                              tag=StackOverflow.Tags.java.value, page_size=100)

link_queue = Queue()
link_queue.put(java_posts)

_kill = threading.Event()

scraper = StackOversight(keys, _kill)
scraper.start(link_queue)
